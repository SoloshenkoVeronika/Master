from __future__ import division

import os
import shutil
from itertools import combinations
from msilib import Binary

import itertools
from pyomo.environ import *
from pyomo.opt import SolverFactory
import math
from .forms import Installation,ERRV
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import shapely.geometry
import pyproj
from pyproj import Proj, transform
import sys
from shapely.geometry import Point, Polygon
import time
number_fix_errv = 0

def get_pot_position(grid):

    all_installations = []
    installation_set = Installation.objects.all()

    for installation in installation_set.iterator():
        field_lat1 = 'latitude'
        field_lon1 = 'longitude'
        single_installation = []
        obj=Installation.objects.get(id=installation.id)
        #print("obj=",obj)
        field_value_lat1 = getattr(obj,  field_lat1)
        field_value_lon1 = getattr(obj,  field_lon1)
        single_installation.append(field_value_lat1)
        single_installation.append(field_value_lon1)
        all_installations.append(single_installation)

    points_all_installations = np.asarray(all_installations, dtype=np.float32)
    #print(all_installations)
    p = list()
    hull = ConvexHull(points_all_installations)
    #print("points",points_all_installations[hull.vertices, 0], points_all_installations[hull.vertices, 1])
    min_x = sys.maxsize
    max_x = -sys.maxsize - 1
    min_y = sys.maxsize
    max_y = -sys.maxsize - 1
    dd = []
    # Получили массив точек из многоугольник
    for i in range(len(hull.vertices)):
        d = []
        tmp_x = points_all_installations[hull.vertices[i],0]
        tmp_y = points_all_installations[hull.vertices[i],1]
        d.append(points_all_installations[hull.vertices[i],0])
        d.append(points_all_installations[hull.vertices[i],1])
        if (tmp_x < min_x):
            min_x = tmp_x
        if (tmp_x > max_x):
            max_x = tmp_x
        if (tmp_y < min_y):
            min_y = tmp_y
        if (tmp_y > max_y):
            max_y = tmp_y
        dd.append(d)

    #print(dd)
    #print(min_x, min_y, max_x, max_y)
    # Сформировали многоугольник
    polygon = Polygon(dd)

    left_side = dd.sort
    #print(left_side)
    # Сформировали сетку
    # Set up projections
    inProj  = Proj("+init=EPSG:3857",preserve_units=True)
    outProj = Proj("+init=EPSG:4326") # WGS84 in degrees and not EPSG:3857 in meters)13

    # Create corners of rectangle to be transformed to a grid
    sw = shapely.geometry.Point((min_x, min_y))
    ne = shapely.geometry.Point((max_x, max_y))

    print("grid_get =", grid)
    grid1 = int(grid)*int(1000)
    print("grid_get1 =", grid1)
    stepsize = grid1 # 5 km grid step size

    stepsizey = int(int(grid1)*2.4)
    print("stepsizey2=",stepsizey)
    transformed_sw = pyproj.transform(outProj, inProj, sw.x, sw.y) # Transform NW point to 3857
    transformed_ne = pyproj.transform(outProj, inProj, ne.x, ne.y) # .. same for SE

    #print("!!!!!!!!!!!!!!",min_x,min_y,max_x, max_y)

    dd = []
    # Iterate over 2D area
    gridpoints = []
    x = transformed_sw[0]
    while x < transformed_ne[0]:
        y = transformed_sw[1]
        while y < transformed_ne[1]:
            p = shapely.geometry.Point(pyproj.transform(inProj, outProj,x, y))
            #print(x,y, " data=",pyproj.transform(inProj,outProj,  x, y))
            gridpoints.append(p)
            d.append(p.x)
            d.append(p.y)
            dd.append(d)
            y += stepsizey
        x += stepsize

    dd = []
    #Проверили, входит ли точка в выпуклый многоульник
    for p in gridpoints:
        d = []
        point = Point(p.x,   p.y)
        pip_mask = point.within(polygon)
        #print(p.x, p.y)
        if (pip_mask):
            d.append(p.x)
            d.append(p.y)
            dd.append(d)
            #print(pip_mask)

    #print(dd)
    return dd

def get_distance(model, i,j):
    #print(model.xcord_i[i]," ",model.xcord_s[j],", ",model.ycord_i[i]," ",model.ycord_s[j])
    xcord_i_r = model.xcord_i[i]*math.pi/180.
    xcord_s_r = model.xcord_s[j]*math.pi/180.
    ycord_i_r = model.ycord_i[i]*math.pi/180.
    ycord_s_r = model.ycord_s[j]*math.pi/180.
    dist = model.radius*(math.acos(math.sin(xcord_i_r)*math.sin(xcord_s_r)+math.cos(xcord_i_r)*math.cos(xcord_s_r)*math.cos(ycord_i_r-ycord_s_r)))
    #print("dist[",i,",",j,"]=",dist)
    return dist

def get_distance_time(model, i,j):
    #a = (model.distance[i,j]/(model.average_speed*model.coef_from))
    #print (i, " ", j, " =",a)
    return (model.distance[i,j]/(model.average_speed*model.coef_from))

def t_validate1(model, i,j):
    #print("md=",model.distance[i,j])
    a=int(model.distance[i,j])/(int(model.average_speed*model.coef_from))
    #print("s=",a)
    #print("at=",int(model.arrive_time[i]))
    if ((int(model.distance[i,j])/(int(model.average_speed*model.coef_from))) <= (int(model.arrive_time[i]))):
        #print(1)
        return 1
    else:
        #print(0)
        return 0

def t_validate2(model, i,j):
    if (int(model.distance_time[i,j]) <= model.arrive_time[i]):
        return 1
    else:
        return 0


def model1(grid,type_errv,ins_fix_list):
    print("model1=", grid, " ins_fix_list=", ins_fix_list,",type_errv=",type_errv)

    #___________________Check get pot position from database or from grid__________________________
    if(type_errv == 2):
        pos_positions = get_pot_position(grid)
        print("pos_positions===",pos_positions)
        lent_pos_positions = len(pos_positions) - pos_positions.count(None)
    elif(type_errv == 1):
        errvs= ERRV.objects.filter(type_solution=210)
        pos_positions = []
        for p in errvs.iterator():
            d = []
            d.append(p.get_lat())
            d.append(p.get_lon())
            pos_positions.append(d)
        lent_pos_positions= len(ERRV.objects.filter(type_solution=210))

    inst = Installation.objects.all()

    #___________________Check is there installation as errv_______________________
    errv_inst_fix = 0
    if (ins_fix_list != 0):
        errv_inst_fix = 1
    errv_inst_fix_lat = 0
    errv_inst_fix_lon = 0

    #___________________Add data to .dat file_______________________
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename = "Model1t.dat"
    filenamemap = "Data_Map.txt"
    FileFullPath = os.path.join(full_path, filename)
    FileFullPathMap = os.path.join(full_path, filenamemap)
    with open(FileFullPath, 'w') as f,open(FileFullPathMap, 'w') as fm:
        f.write("set INSTALLATION := ")
        for p in inst:
            # ______________ -start- Only for installation as errv
            if(p.get_id()==int(ins_fix_list)):
                errv_inst_fix_lat = p.get_lat()
                errv_inst_fix_lon = p.get_lon()
            # ______________ -end-
            f.write(str(p.get_title())+" ")
        f.write(";\n")
        f.write("set SITE  := ")
        count_p = 0
        for p in range(lent_pos_positions):
            f.write(str("ERRV_"+str(p)))
            f.write(str(" "))
            count_p = count_p + 1
        # ______________ -start- Only for installation as errv
        if (errv_inst_fix != 0):
            global number_fix_errv
            number_fix_errv = count_p
            f.write(str("ERRV_"+str(count_p)))
        # ______________ -end-
        f.write(";\n")
        f.write("param radius := 6371;\n")
        f.write("param coef_from := 1.825;\n")
        f.write("param average_speed := 17;\n")
        f.write("param :     arrive_time xcord_i ycord_i:= \n")
        fm.write("ELEV,LAT,LON,NAME\n")
        for p in inst:
            time = p.get_r_time()
            time=time - 1
            #____________________________ Time 5
            # if (time==3):
            #     time = 5
            # else:
            #     time = p.get_r_time()-1
            #____________________________ Time 5
            f.write(str(p.get_title())+" "+str(time)+"   "+str(p.get_lat())+"   "+str(p.get_lon())+"\n")
            fm.write(str(1)+",   "+str(p.get_lat())+",   "+str(p.get_lon())+",   "+str(p.get_title())+"\n")
        f.write(";\n")
        f.write("param : 	xcord_s ycord_s:= \n")

        i=0
        for p in pos_positions:
            f.write(str("ERRV_"+str(i)+" "+(str(pos_positions.__getitem__(i))).replace('[','').replace(']','').replace(',','')+"\n"))
            fm.write(str(2)+",   "+str(pos_positions.__getitem__(i)).replace('[','').replace(']','')+"\n")
            i+=1
            f.write(str(" "))
        if (errv_inst_fix != 0):
            f.write(str("ERRV_"+str(i)+" "+str(errv_inst_fix_lat)+" "+str(errv_inst_fix_lon)))

        # for p in errv:
        #     f.write(str(p.get_title())+" "+str(p.get_lat())+"   "+str(p.get_lon())+"\n")

        f.write(";\n")

    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.y = Var(model.SITE, domain = Binary)
    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate1)

    def obj_expression(model):
        return sum(model.y[j] for j in model.SITE)

    model.obj = Objective(rule=obj_expression, sense=minimize)

    def Balance(model,i):
        return sum(model.aa[i,j]*model.y[j] for j in model.SITE) >= 1

    model.con = Constraint(model.INSTALLATION, rule=Balance)

    # ______________ -start- Only for installation as errv
    if (ins_fix_list != 0):
        def Balance_Fix(model):
            return (model.y[str('ERRV_')+str(number_fix_errv)] == 1)
        model.con2 = Constraint(rule=Balance_Fix)
    # ______________ -end-
    data = DataPortal()
    data.load(filename='main\\recources\\Model1t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model1t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model1t.dat', param=(model.distance,
                                                              model.arrive_time,
                                                              model.coef_from,
                                                              model.average_speed,
                                                              model.xcord_s,
                                                              model.ycord_s,
                                                              model.xcord_i,
                                                              model.ycord_i))

    # create a model instance and optimise
    instance = model.create_instance(data)
    solvername='cbc'

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)

    results = opt.solve(instance)
    instance.solutions.store_to(results)
    # for i in instance.INSTALLATION:
    #     for j in instance.SITE:
    #         print('Done')
            #print(str(instance.aa[i,j])+ " ")


    # if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    #     #print('Do something when the solution in optimal and feasible')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.aa[i,j] ,end =" ")
    #         print("")
    #     for j in instance.SITE:
    #         print('y[',j,']=' , instance.y[j].value)
    #     print('___Total cost___')
    #     print(value(instance.obj))
    # elif (results.solver.termination_condition == TerminationCondition.infeasible):
    #     print('Model is infeasible')
    # else:
    #     # Something else is wrong
    #     print('Solver Status: ',  results.solver.status)

    filename_results = "Model1t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)

    with open(FileFullPathResults, 'w') as f:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y="+"\n")
        for j in instance.SITE:
            f.write(str(instance.y[j].value)+ " ")
        f.write("\n")


    count_errv = 0
    for j in instance.SITE:
        if(instance.y[j].value == 1):
            count_errv+=1

    original = FileFullPath
    filename2 = "Model2t.dat"
    filename3 = "Model3t.dat"
    filename4 = "Model4t.dat"
    filename5 = "Model5t.dat"
    filename6 = "Modelpotpos.dat"
    FileFullPath2 = os.path.join(full_path, filename2)
    target2 = FileFullPath2
    FileFullPath3 = os.path.join(full_path, filename3)
    target3 = FileFullPath3
    FileFullPath4 = os.path.join(full_path, filename4)
    target4 = FileFullPath4
    FileFullPath5 = os.path.join(full_path, filename5)
    target5 = FileFullPath5
    FileFullPath6 = os.path.join(full_path, filename6)
    target6 = FileFullPath6
    shutil.copyfile(original, target2)
    shutil.copyfile(original, target3)
    shutil.copyfile(original, target4)
    shutil.copyfile(original, target5)
    with open(FileFullPath2, 'a') as f2,open(FileFullPath3, 'a') as f3,open(FileFullPath4, 'a') as f4,open(FileFullPath5, 'a') as f5:
        f2.write("param vessels_number := " + str(count_errv))
        f2.write(";\n")
        f3.write("param vessels_number := " + str(count_errv))
        f3.write(";\n")
        f4.write("param vessels_number := " + str(count_errv))
        f4.write(";\n")
        f4.write("set VESSELS := ")
        for i in range(count_errv):
            f4.write(" VESSEL_"+str(i)+" ")
        f4.write(";\n")
        f5.write("param vessels_number := " + str(count_errv))
        f5.write(";\n")
        f5.write("set VESSELS := ")
        for i in range(count_errv):
            f5.write(" VESSEL_"+str(i)+" ")
        f5.write(";\n")

    # with open(FileFullPath5, 'w') as f:
    #     f.write("set INSTALLATION := ")
    #     for p in inst:
    #         f.write(str(p.get_title())+" ")
    #     f.write(";\n")
    #     f.write("set SITE  := ")
    #     for p in range(lent_pos_positions):
    #         f.write(str("ERRV_"+str(p)))
    #         f.write(str(" "))
    #
    #     f.write(";\n")
    #     f.write("param radius := 6371;\n")
    #     f.write("param coef_from := 1.825;\n")
    #     f.write("param average_speed := 17;\n")
    #     f.write("param vessels_number := " + str(count_errv))
    #     f.write(";\n")
    #
    #     f.write("param :     arrive_time xcord_i ycord_i   consequence	threat:=  \n")
    #     for p in inst:
    #         f.write(str(p.get_title())+" "+str(p.get_r_time())+"   "+str(p.get_lat())+"   "+str(p.get_lon())+"   "+str(p.get_people())+"   "+str(p.get_c_accident())+"\n")
    #     f.write(";\n")



    print("Done1")

    with open(FileFullPath6, 'w') as f:
        i=0
        for p in pos_positions:
            f.write(str("ERRV_"+str(i)+" "+(str(pos_positions.__getitem__(i))).replace('[','').replace(']','').replace(',','')+"\n"))
            i+=1


    # i=0
    # with open(FileFullPath6, 'w') as f:
    #     for j in instance.SITE:
    #         if(instance.y[j].value==1):
    #             f.write(str("ERRV_"+str(i)+" "+str(instance.ycord_s[j])+" "+str(instance.xcord_s[j])+"\n"))
    #             i+=1


    return count_errv


def model2(ins_fix_list,flag_model4):
    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()
    model.vessels_number= Param()

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.distance_time= Param(model.INSTALLATION, model.SITE, initialize=get_distance_time)

    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate2)

    model.y = Var(model.SITE, domain = Binary)
    model.x = Var(model.INSTALLATION,model.SITE, domain = Binary)


    def obj_expression(model):
        return sum(model.distance_time[i,j]*model.x[i,j] for i in model.INSTALLATION for j in model.SITE)


    model.obj = Objective(rule=obj_expression, sense=minimize)


    def Balance(model,i):
        return sum(model.aa[i,j]*model.x[i,j] for j in model.SITE) >= 1

    def Balance2(model):
        return sum(model.y[j] for j in model.SITE) == model.vessels_number

    def Balance3(model,i,j):
        return model.x[i,j] <= model.y[j]

    # the next line creates one constraint for each member of the set model.I
    model.con1 = Constraint(model.INSTALLATION, rule=Balance)
    model.con2 = Constraint(rule=Balance2)
    model.con3 = Constraint(model.INSTALLATION,model.SITE,rule=Balance3)

    # ______________ -start- Only for installation as errv
    if (ins_fix_list != 0):
        def Balance_Fix(model):
            return (model.y[str('ERRV_')+str(number_fix_errv)] == 1)
        model.con4 = Constraint(rule=Balance_Fix)
    # ______________ -end-


    # load data
    data = DataPortal()
    data.load(filename='main\\recources\\Model2t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model2t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model2t.dat', param=(model.distance,
                                                              model.arrive_time,
                                                              model.coef_from,
                                                              model.average_speed,
                                                              model.xcord_s,
                                                              model.ycord_s,
                                                              model.xcord_i,
                                                              model.ycord_i,
                                                              model.vessels_number))

    # create a model instance and optimise
    instance = model.create_instance(data)

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)

    results = opt.solve(instance)
    instance.solutions.store_to(results)
    # if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    #     print('___aa___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.aa[i,j] ,end =" ")
    #         print("")
    #     print('___x___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.x[i,j].value ,end =" ")
    #         print("")
    #     print('___y___')
    #     for j in instance.SITE:
    #         print('y[',j,']=' , instance.y[j].value)
    #     print('___Total cost___')
    #     print(value(instance.obj))
    #     #print('Do something when the solution in optimal and feasible')
    #
    #
    # elif (results.solver.termination_condition == TerminationCondition.infeasible):
    #     print('Model is infeasible')
    # else:
    #     # Something else is wrong
    #     print('Solver Status: ',  result.solver.status)

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model2t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    filename_results_map = "Data_Map.txt"
    FileFullPathMap = os.path.join(full_path, filename_results_map)
    filename_results_map_errv = "Data_Map_ERRV.txt"
    FileFullPathMap_errv = os.path.join(full_path, filename_results_map_errv)
    with open(FileFullPathResults, 'w') as f,open(FileFullPathMap, 'a') as fm,open(FileFullPathMap_errv, 'w') as fmerrv:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("X="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.x[i,j].value)+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y=")
        for j in instance.SITE:
            f.write(str(instance.y[j].value)+ " ")
        f.write("\n")
        fmerrv.write("ELEV,LAT,LON\n")

        for j in instance.SITE:
            if(instance.y[j].value==1):
                f.write("O_" +str(j)+ " "+str(instance.xcord_s[j])+ " "+str(instance.ycord_s[j])+" 1\n")
                # ______________ -start- Only for installation as errv
                if flag_model4 != 1:
                    if (ins_fix_list != 0):
                        if (j == (str('ERRV_')+str(number_fix_errv))):
                            print("j=",j,"  model.y[str('ERRV_')+str(number_fix_errv)]=", str('ERRV_')+str(number_fix_errv))
                            fm.write(str(100)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        else:
                            fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        # ______________ -end-
                    else:
                        fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fm.write("\n")
                    #fmerrv.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(5)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(6)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
        f.write("\n")

    #____________start  .dat file for multi (model4)__________

    filename5 = "Model5t.dat"
    FileFullPath5 = os.path.join(full_path, filename5)
    with open(FileFullPath5, 'a') as f5:
        f5.write("param goal_avg := "+str(value(instance.obj))+";\n")
    #____________end  .dat file for multi (model4)__________


    ERRV.objects.filter(type_solution=202).delete()
    for j in instance.SITE:
        if(instance.y[j].value==1):
            errv = ERRV(title="TT_" +str(j), latitude=instance.xcord_s[j],longitude=instance.ycord_s[j],prob=0.0,type_solution=202)
            errv.save()

    print('Done2')

def model3(ins_fix_list,flag_model4):

    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()
    model.vessels_number= Param()

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.distance_time= Param(model.INSTALLATION, model.SITE, initialize=get_distance_time)
    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate2)

    # the next line declares a variable indexed by the set J
    model.y = Var(model.SITE, domain = Binary)
    model.x = Var(model.INSTALLATION,model.SITE, domain = Binary)
    model.t = Var(domain = NonNegativeReals)

    def obj_expression(model):
        return model.t
    model.obj = Objective(rule=obj_expression, sense=minimize)


    def Balance(model,i):
        return sum(model.aa[i,j]*model.x[i,j] for j in model.SITE) >= 1

    def Balance2(model):
        return sum(model.y[j] for j in model.SITE) == model.vessels_number

    def Balance3(model,i,j):
        return model.x[i,j] <= model.y[j]

    def Balance4(model,i,j):
        return model.distance_time[i,j]*model.x[i,j] <= model.t


    model.con1 = Constraint(model.INSTALLATION, rule=Balance)
    model.con2 = Constraint(rule=Balance2)
    model.con3 = Constraint(model.INSTALLATION,model.SITE,rule=Balance3)
    model.con4 = Constraint(model.INSTALLATION,model.SITE,rule=Balance4)

    # ______________ -start- Only for installation as errv
    if (ins_fix_list != 0):
        def Balance_Fix(model):
            return (model.y[str('ERRV_')+str(number_fix_errv)] == 1)
        model.con5 = Constraint(rule=Balance_Fix)
    # ______________ -end-

    # load data
    data = DataPortal()
    data.load(filename='main\\recources\\Model3t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model3t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model3t.dat', param=(model.distance,
                                                                  model.arrive_time,
                                                                  model.coef_from,
                                                                  model.average_speed,
                                                                  model.xcord_s,
                                                                  model.ycord_s,
                                                                  model.xcord_i,
                                                                  model.ycord_i,
                                                                  model.vessels_number))

    # create a model instance and optimise
    instance = model.create_instance(data)

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    #results.write()
    #instance.display()

    # if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    #     print('___aa___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.aa[i,j] ,end =" ")
    #         print("")
    #     print('___x___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.x[i,j].value ,end =" ")
    #         print("")
    #     print('___y___')
    #     for j in instance.SITE:
    #         print('y[',j,']=' , instance.y[j].value)
    #     print('___Total cost___')
    #     print(value(instance.obj))
    #     #print('Do something when the solution in optimal and feasible')
    #
    #
    # elif (results.solver.termination_condition == TerminationCondition.infeasible):
    #     print('Model is infeasible')
    # else:
    #     # Something else is wrong
    #     print('Solver Status: ',  result.solver.status)

    print('Done3')

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model3t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    sum_time = 0.0
    with open(FileFullPathResults, 'w') as f:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
               sum_time += instance.distance_time[i,j]*instance.x[i,j].value
        f.write("Total time="+str(sum_time)+ " "+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("X="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.x[i,j].value)+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y=")
        for j in instance.SITE:
            f.write(str(instance.y[j].value)+ " ")
        f.write("\n")
        for j in instance.SITE:
            if(instance.y[j].value==1):
                f.write("O_" +str(j)+ " "+str(instance.xcord_s[j])+ " "+str(instance.ycord_s[j])+" 1 \n")

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_resultserrv = "Model3terrv.sol"
    FileFullPathResults = os.path.join(full_path, filename_resultserrv)
    filename_results_map = "Data_Map.txt"
    FileFullPathMap = os.path.join(full_path, filename_results_map)
    filename_results_map_errv = "Data_Map_ERRV.txt"
    FileFullPathMap_errv = os.path.join(full_path, filename_results_map_errv)

    number_errv = 1
    with open(FileFullPathResults, 'w') as f,open(FileFullPathMap, 'a') as fm,open(FileFullPathMap_errv, 'w') as fmerrv:
        fmerrv.write("ELEV,LAT,LON\n")
        for j in instance.SITE:
            #print (instance.y[j].value)
            if (instance.y[j].value == 1.0):
                f.write(str(number_errv))
                if flag_model4 != 1:
                    # ______________ -start- Only for installation as errv
                    if (ins_fix_list != 0):
                        if (j == (str('ERRV_')+str(number_fix_errv))):
                            print("j=",j,"  model.y[str('ERRV_')+str(number_fix_errv)]=", str('ERRV_')+str(number_fix_errv))
                            fm.write(str(100)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        else:
                            fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                            # ______________ -end-
                    else:
                        fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fm.write("\n")
                    #fmerrv.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(5)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(6)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    f.write("\n")
            number_errv+=1
    ERRV.objects.filter(type_solution=203).delete()
    for j in instance.SITE:
        if(instance.y[j].value==1):
            errv = ERRV(title="WT_" +str(j), latitude=instance.xcord_s[j],longitude=instance.ycord_s[j],prob=0.0,type_solution=203)
            errv.save()

#____________start  .dat file for multi (model4)__________

    filename4 = "Model5t.dat"
    FileFullPath4 = os.path.join(full_path, filename4)
    with open(FileFullPath4, 'a') as f4:
        f4.write("param goal_worst := "+str(value(instance.obj))+";\n")
#____________end  .dat file for multi (model4)__________


    filename_resultserrv = "Model1t.sol"
    FileFullPathResults = os.path.join(full_path, filename_resultserrv)
    # with open(FileFullPathResults, 'r') as f:
    #     for x in f:
    #         errvs = ERRV.objects.filter(id=int(x))
    # # errvs = ERRV.objects.filter(id=2)
    # errvs = ERRV.objects.order_by('id')

def model4(ins_fix_list,flag_model4):
    print("RISR Model 4")
    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()
    model.VESSELS = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()
    model.vessels_number= Param()
    model.crash_probability = Param(model.VESSELS)

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.distance_time= Param(model.INSTALLATION, model.SITE, initialize=get_distance_time)

    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate2)

    model.y = Var(model.SITE,model.VESSELS, domain = Binary)
    model.x = Var(model.INSTALLATION,model.SITE,model.VESSELS, domain = Binary)


    def obj_expression(model):
        return sum(model.crash_probability[v]*model.x[i,j,v] for i in model.INSTALLATION for j in model.SITE for v in model.VESSELS)


    model.obj = Objective(rule=obj_expression, sense=minimize)


    def Balance(model,i):
        return sum(model.aa[i,j]*model.x[i,j,v] for j in model.SITE for v in model.VESSELS) >= 1

    def Balance2(model,i,j,v):
        return model.x[i,j,v] <= model.y[j,v]

    def Balance3(model,v):
        return sum(model.y[j,v] for j in model.SITE) == 1

    def Balance4(model,j):
        return sum(model.y[j,v] for v in model.VESSELS) <= 1

    # the next line creates one constraint for each member of the set model.I
    model.con1 = Constraint(model.INSTALLATION, rule=Balance)
    model.con2 = Constraint(model.INSTALLATION,model.SITE,model.VESSELS, rule=Balance2)
    model.con3 = Constraint(model.VESSELS,rule=Balance3)
    model.con4 = Constraint(model.SITE,rule=Balance4)

    # ______________ -start- Only for installation as errv
    # print("ins_fix_list=",ins_fix_list)
    # if (ins_fix_list != 0):
    #     def Balance_Fix(model):
    #         return (model.y[str('ERRV_')+str(number_fix_errv)] == 1)
    #     model.con5 = Constraint(rule=Balance_Fix)
    # ______________ -end-


    # load data
    data = DataPortal()
    data.load(filename='main\\recources\\Model4t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model4t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model4t.dat', set=model.VESSELS)
    data.load(filename='main\\recources\\Model4t.dat', param=(model.distance,
                                                              model.arrive_time,
                                                              model.coef_from,
                                                              model.average_speed,
                                                              model.xcord_s,
                                                              model.ycord_s,
                                                              model.xcord_i,
                                                              model.ycord_i,
                                                              model.vessels_number,
                                                              model.crash_probability))

    # create a model instance and optimise
    instance = model.create_instance(data)

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)

    results = opt.solve(instance)
    instance.solutions.store_to(results)


    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model4t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    filename_results_map = "Data_Map.txt"
    FileFullPathMap = os.path.join(full_path, filename_results_map)
    filename_results_map_errv = "Data_Map_ERRV.txt"
    FileFullPathMap_errv = os.path.join(full_path, filename_results_map_errv)
    with open(FileFullPathResults, 'w') as f,open(FileFullPathMap, 'a') as fm,open(FileFullPathMap_errv, 'w') as fmerrv:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:

            for j in instance.SITE:
                f.write(str([i,j])+ " ")
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("X="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                for v in instance.VESSELS:
                    f.write(str(instance.x[i,j,v].value)+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y=")
        for j in instance.SITE:
            for v in instance.VESSELS:
                f.write(str(instance.y[j,v].value)+ " ")
            f.write("\n")
        f.write("\n")
        fmerrv.write("ELEV,LAT,LON\n")

        for j in instance.SITE:
            for v in instance.VESSELS:
                if(instance.y[j,v].value==1):
                    f.write("O_" +str(j)+ " "+str(instance.xcord_s[j])+ " "+str(instance.ycord_s[j])+" 1")
                    # ______________ -start- Only for installation as errv
                    if flag_model4 != 1:
                        if (ins_fix_list != 0):
                            if (j == (str('ERRV_')+str(number_fix_errv))):
                                print("j=",j,"  model.y[str('ERRV_')+str(number_fix_errv)]=", str('ERRV_')+str(number_fix_errv))
                                fm.write(str(100)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                            else:
                                fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                                # ______________ -end-
                        else:
                            fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        fm.write("\n")
                        #fmerrv.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        fmerrv.write("\n")
                        fmerrv.write(str(5)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        fmerrv.write("\n")
                        fmerrv.write(str(6)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        fmerrv.write("\n")
        f.write("\n")

    #____________start  .dat file for multi (model4)__________

    filename5 = "Model5t.dat"
    FileFullPath5 = os.path.join(full_path, filename5)
    with open(FileFullPath5, 'a') as f5:
        f5.write("param goal_risk := "+str(value(instance.obj))+";\n")
    #____________end  .dat file for multi (model4)__________


    ERRV.objects.filter(type_solution=202).delete()
    for j in instance.SITE:
        for v in instance.VESSELS:
            if(instance.y[j,v].value==1):
                errv = ERRV(title="TT_" +str(j), latitude=instance.xcord_s[j],longitude=instance.ycord_s[j],prob=0.0,type_solution=202)
                errv.save()

    print('Done4')


def model5(ins_fix_list,wa,ww,wr):

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    #____________start  .dat file for multi (model4)__________

    filename4 = "Model5t.dat"
    FileFullPath4 = os.path.join(full_path, filename4)
    with open(FileFullPath4, 'a') as f4:
        f4.write("param e_avg := "+str(wa)+";\n")
        f4.write("param e_worst := "+str(ww)+";\n")
        f4.write("param e_risk := "+str(wr)+";\n")
    #____________end  .dat file for multi (model4)__________

    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()
    model.VESSELS = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()
    model.vessels_number = Param()
    model.crash_probability = Param(model.VESSELS)

    model.goal_avg= Param()
    model.goal_worst= Param()
    model.goal_risk = Param()
    model.e_avg= Param()
    model.e_worst= Param()
    model.e_risk= Param()

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.distance_time= Param(model.INSTALLATION, model.SITE, initialize=get_distance_time)
    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate2)

    # the next line declares a variable indexed by the set J
    model.y = Var(model.SITE,model.VESSELS, domain = Binary)
    model.x = Var(model.INSTALLATION,model.SITE,model.VESSELS, domain = Binary)
    model.t = Var(domain = NonNegativeReals) #variable for worst case
    model.q = Var(domain = NonNegativeReals) #combined target value

    def obj_expression(model):
        return model.q
    model.obj = Objective(rule=obj_expression, sense=minimize)


    def Balance(model,i):
        return sum(model.aa[i,j]*model.x[i,j,v] for j in model.SITE for v in model.VESSELS) >= 1

    def Balance2(model):
        return sum(model.y[j,v] for j in model.SITE for v in model.VESSELS) == model.vessels_number

    def Balance3(model,i,j,v):
        return model.x[i,j,v] <= model.y[j,v]

    def vessel_position1(model, v):
        return sum (model.y[j,v] for j in model.SITE) == 1

    def vessel_position2 (model, j):
        return sum (model.y[j,v] for v in model.VESSELS)  <= 1

    def Balance4(model,i,j,v):
        return model.distance_time[i,j]*model.x[i,j,v] <= model.t

    def Balance5(model):
        return model.e_avg * ( (-1) * model.goal_avg + sum (model.x[i,j,v]*model.distance_time[i,j] for i in model.INSTALLATION for j in model.SITE  for v in model.VESSELS ))/model.goal_avg <= model.q
    def Balance6(model):
        return model.e_worst * (model.t - model.goal_worst)/model.goal_worst <= model.q

    def Limit_max_deviation_risk(model):
        return model.e_risk * ((sum ( model.x[i,j,v]*model.crash_probability[v] for i in model.INSTALLATION for j in model.SITE for v in model.VESSELS)) - model.goal_risk)/model.goal_risk <= model.q


    def Balance7(model):
        return 0 <= model.q



    model.con1 = Constraint(model.INSTALLATION, rule=Balance)
    model.con2 = Constraint(rule=Balance2)
    model.con3 = Constraint(model.INSTALLATION,model.SITE,model.VESSELS,rule=Balance3)
    model.con4 = Constraint(model.INSTALLATION,model.SITE,model.VESSELS,rule=Balance4)
    model.con5 = Constraint(rule=Balance5)
    model.con6 = Constraint(rule=Balance6)
    model.con7 = Constraint(rule=Balance7)
    model.con8 = Constraint(model.VESSELS,rule=vessel_position1)
    model.con9 = Constraint(model.SITE,rule=vessel_position2)
    model.con10 = Constraint(rule=Limit_max_deviation_risk)
    # ______________ -start- Only for installation as errv
    # if (ins_fix_list != 0):
    #     def Balance_Fix(model):
    #         return (model.y[str('ERRV_')+str(number_fix_errv)] == 1)
    #     model.con5 = Constraint(rule=Balance_Fix)
    # ______________ -end-

    # load data
    data = DataPortal()
    data.load(filename='main\\recources\\Model5t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model5t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model5t.dat', set=model.VESSELS)
    data.load(filename='main\\recources\\Model5t.dat', param=(model.distance,
                                                              model.arrive_time,
                                                              model.coef_from,
                                                              model.average_speed,
                                                              model.xcord_s,
                                                              model.ycord_s,
                                                              model.xcord_i,
                                                              model.ycord_i,
                                                              model.vessels_number,
                                                              model.goal_avg,
                                                              model.goal_worst,
                                                              model.goal_risk ,
                                                              model.e_avg,
                                                              model.e_worst,
                                                              model.e_risk,
                                                              model.crash_probability))

    # create a model instance and optimise
    instance = model.create_instance(data)

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)
    results = opt.solve(instance)
    instance.solutions.store_to(results)

    filename_results = "Model5t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    sum_time = 0.0
    sum_risk = 0.0
    with open(FileFullPathResults, 'w') as f:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                for v in instance.VESSELS:
                    sum_time += instance.distance_time[i,j]*instance.x[i,j,v].value
                    sum_risk += instance.crash_probability[v]*instance.x[i,j,v].value
        f.write("Total time="+str(sum_time)+ " "+"\n")
        f.write("Total risk="+str(sum_risk)+ " "+"\n")
        f.write("T="+str(instance.t.value)+ " "+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("X="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                for v in instance.VESSELS:
                    f.write(str(instance.x[i,j,v].value)+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y=")
        for j in instance.SITE:
            for v in instance.VESSELS:
                f.write(str(instance.y[j,v].value)+ " ")
        f.write("\n")
        for j in instance.SITE:
            for v in instance.VESSELS:
                if(instance.y[j,v].value==1):
                    f.write("Multi_" +str(j)+ " "+str(instance.xcord_s[j])+ " "+str(instance.ycord_s[j])+" 1 \n")

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_resultserrv = "Model4terrv.sol"
    FileFullPathResults = os.path.join(full_path, filename_resultserrv)
    filename_results_map = "Data_Map.txt"
    FileFullPathMap = os.path.join(full_path, filename_results_map)
    filename_results_map_errv = "Data_Map_ERRV.txt"
    FileFullPathMap_errv = os.path.join(full_path, filename_results_map_errv)

    number_errv = 1
    with open(FileFullPathResults, 'w') as f,open(FileFullPathMap, 'a') as fm,open(FileFullPathMap_errv, 'w') as fmerrv:
        fmerrv.write("ELEV,LAT,LON\n")
        for j in instance.SITE:
            for v in instance.VESSELS:
            #print (instance.y[j].value)
                if (instance.y[j,v].value == 1.0):
                    f.write(str(number_errv))
                    # ______________ -start- Only for installation as errv
                    if (ins_fix_list != 0):
                        if (j == (str('ERRV_')+str(number_fix_errv))):
                            print("j=",j,"  model.y[str('ERRV_')+str(number_fix_errv)]=", str('ERRV_')+str(number_fix_errv))
                            fm.write(str(100)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                        else:
                            fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                            # ______________ -end-
                    else:
                        fm.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fm.write("\n")
                   # fmerrv.write(str(3)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(5)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    fmerrv.write(str(6)+", "+str(instance.xcord_s[j])+ ", "+str(instance.ycord_s[j]))
                    fmerrv.write("\n")
                    f.write("\n")
                number_errv+=1
    ERRV.objects.filter(type_solution=204).delete()
    for j in instance.SITE:
        for v in instance.VESSELS:
            if(instance.y[j,v].value==1):
                errv = ERRV(title="Multi_" +str(j), latitude=instance.xcord_s[j],longitude=instance.ycord_s[j],prob=0.0,type_solution=204)
                errv.save()


    print("Done4")




def model_risk(wr,wt):

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")

    filename2 = "Model5t.dat"
    FileFullPath52 = os.path.join(full_path, filename2)

    filenamepos = "Modelpotpos.dat"
    FileFullPathPos = os.path.join(full_path, filenamepos)

    # with open(FileFullPath5,'r+') as fr,open(FileFullPath52,'w') as fw:
    #     for line in fr:
    #         x = line.find('param : 	xcord_s ycord_s:= ')
    #         if(x==-1):
    #             fw.write(line)
    #         else:
    #             fw.write(line[0:x])
    #             break
    #     fw.truncate()

    filenameprob = "Probability.txt"
    FileFullPathProb = os.path.join(full_path, filenameprob)

    with open(FileFullPathPos, 'r') as f1, open(FileFullPathProb, 'r') as f2, open(FileFullPath52, 'a') as f3:
        f3.write("param : 	xcord_s ycord_s  vulnerability := ")
        f3.write("\n")
        for p in zip(f1, f2):
            print(*map(lambda s: s.strip(), p), sep=' ', file=f3)
        f3.write(";\n")
        f3.write("param wr := " + str(wr))
        f3.write(";\n")
        f3.write("param wt := " + str(wt))
        f3.write(";\n")

    model = AbstractModel()

    model.INSTALLATION = Set()
    model.SITE = Set()

    model.arrive_time = Param(model.INSTALLATION)
    model.coef_from = Param()
    model.average_speed = Param()

    model.xcord_s = Param(model.SITE)
    model.ycord_s = Param(model.SITE)
    model.xcord_i = Param(model.INSTALLATION)
    model.ycord_i = Param(model.INSTALLATION)
    model.radius = Param()
    model.vessels_number= Param()

    model.consequence = Param(model.INSTALLATION)
    model.threat = Param(model.INSTALLATION)
    model.vulnerability = Param(model.SITE)

    model.wt = Param(domain = NonNegativeReals)
    model.wr = Param(domain = NonNegativeReals)

    model.distance = Param(model.INSTALLATION, model.SITE, initialize=get_distance)
    model.distance_time= Param(model.INSTALLATION, model.SITE, initialize=get_distance_time)
    model.aa = Param(model.INSTALLATION, model.SITE, initialize=t_validate2)

    # the next line declares a variable indexed by the set J
    model.y = Var(model.SITE, domain = Binary)
    model.x = Var(model.INSTALLATION,model.SITE, domain = Binary)
    model.t = Var(domain = NonNegativeReals)
    model.r = Var(domain = NonNegativeReals)

    def obj_expression(model):
        return (model.t*model.wt+model.r*model.wr)
    model.obj = Objective(rule=obj_expression, sense=minimize)


    def Balance(model,i):
        return sum(model.aa[i,j]*model.x[i,j] for j in model.SITE) >= 1

    def Balance2(model):
        return sum(model.y[j] for j in model.SITE) == model.vessels_number

    def Balance3(model,i,j):
        return model.x[i,j] <= model.y[j]

    def Balance4(model):
        return sum(model.distance_time[i,j]*model.x[i,j] for i in model.INSTALLATION for j in model.SITE) <= model.t


    def Balance5(model,i):
        return (log10(model.consequence[i]*model.threat[i])+sum(log10(1-model.aa[i,j]+model.vulnerability[j]*model.aa[i,j])*model.y[j] for j in model.SITE)) <= model.r

    model.con1 = Constraint(model.INSTALLATION, rule=Balance)
    model.con2 = Constraint(rule=Balance2)
    model.con3 = Constraint(model.INSTALLATION,model.SITE,rule=Balance3)
    model.con4 = Constraint(rule=Balance4)
    model.con5 = Constraint(model.INSTALLATION,rule=Balance5)



    # load data
    data = DataPortal()
    data.load(filename='main\\recources\\Model5t.dat', set=model.INSTALLATION)
    data.load(filename='main\\recources\\Model5t.dat', set=model.SITE)
    data.load(filename='main\\recources\\Model5t.dat', param=(model.distance,
                                                              model.arrive_time,
                                                              model.coef_from,
                                                              model.average_speed,
                                                              model.xcord_s,
                                                              model.ycord_s,
                                                              model.xcord_i,
                                                              model.ycord_i,
                                                              model.vessels_number,
                                                              model.consequence,
                                                              model.threat,
                                                              model.vulnerability,
                                                              model.wr,
                                                              model.wt))

    # create a model instance and optimise
    instance = model.create_instance(data)

    solverpath_exe='main\\recources\\cbc.exe' #does not need to be directly on c drive

    opt = SolverFactory('cbc',executable=solverpath_exe)
    results = opt.solve(instance)
    instance.solutions.store_to(results)
    #results.write()
    #instance.display()

    # if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    #     print('___aa___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.aa[i,j] ,end =" ")
    #         print("")
    #     print('___x___')
    #     for i in instance.INSTALLATION:
    #         for j in instance.SITE:
    #             print(instance.x[i,j].value ,end =" ")
    #         print("")
    #     print('___y___')
    #     for j in instance.SITE:
    #         print('y[',j,']=' , instance.y[j].value)
    #     print('___Total cost___')
    #     print(value(instance.obj))
    #     #print('Do something when the solution in optimal and feasible')
    #
    #
    # elif (results.solver.termination_condition == TerminationCondition.infeasible):
    #     print('Model is infeasible')
    # else:
    #     # Something else is wrong
    #     print('Solver Status: ',  result.solver.status)

    print('Done4')

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model5t.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)

    with open(FileFullPathResults, 'w') as f:
        f.write("Total cost="+str(value(instance.obj))+"\n")
        f.write("Coverage parameter="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.aa[i,j])+ " ")
            f.write("\n")
        f.write("\n")
        f.write("X="+"\n")
        for i in instance.INSTALLATION:
            for j in instance.SITE:
                f.write(str(instance.x[i,j].value)+ " ")
            f.write("\n")
        f.write("\n")
        f.write("Y="+"\n")
        for j in instance.SITE:
            f.write(str(instance.y[j].value)+ " ")
        f.write("\n")

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_resultserrv = "Model3terrv.sol"
    FileFullPathResults = os.path.join(full_path, filename_resultserrv)

    number_errv = 1
    with open(FileFullPathResults, 'w') as f:
        for j in instance.SITE:
            #print (instance.y[j].value)
            if (instance.y[j].value == 1.0):
                f.write(str(number_errv))
                f.write("\n")
            number_errv+=1

    filename_resultserrv = "Model1t.sol"
    ERRV.objects.filter(type_solution=205).delete()
    for j in instance.SITE:
        if(instance.y[j].value==1):
            errv = ERRV(title="Risk_" +str(j), latitude=instance.xcord_s[j],longitude=instance.ycord_s[j],prob=0.001,type_solution=205)
            errv.save()
    FileFullPathResults = os.path.join(full_path, filename_resultserrv)
    # with open(FileFullPathResults, 'r') as f:
    #     for x in f:
    #         errvs = ERRV.objects.filter(id=int(x))
    # # errvs = ERRV.objects.filter(id=2)
    # errvs = ERRV.objects.order_by('id')


def crush_prob(t,errvs):
    result = list()
    for errv_age in errvs:
        result.append(1 - math.exp(-0.00027397260273973 * (1 + 0.33 * errv_age) * pow(int(t),2)))

    filename4 = "Model4t.dat"
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    FileFullPath4 = os.path.join(full_path, filename4)


    with open(FileFullPath4, 'a') as f4:
        f4.write("param: crash_probability:=")
        f4.write("\n")

    with open(FileFullPath4, 'a') as f5:
        j = 0
        for i in result:
            f5.write("VESSEL_"+str(j)+"   "+str(i)+"\n")
            j+=1
        f5.write(";\n")


    filename5 = "Model5t.dat"
    FileFullPath5 = os.path.join(full_path, filename5)


    with open(FileFullPath5, 'a') as f5:
        f5.write("param: crash_probability:=")
        f5.write("\n")

    with open(FileFullPath5, 'a') as f5:
        j = 0
        for i in result:
            f5.write("VESSEL_"+str(j)+"   "+str(i)+"\n")
            j+=1
        f5.write(";\n")

    return result