import math
import random
import cv2
import numpy as np
import torch
from scipy.interpolate import splprep, splev
import copy
from shapely.geometry import Point, Polygon
from scipy.spatial import Delaunay
from collections import deque

def draw_circle(image, center, radius, color):
    h, w = image.shape
    Y, X = np.ogrid[:h, :w]
    image1 = copy.deepcopy(image)
    # if color == 'white':
    #     image1 = np.zeros_like(image1)
    mask = (X - center[0])**2 + (Y - center[1])**2 <= radius**2
    image1[mask] = 255 if color=='white' else 0
    return image1

def white_intersection_area(image1, image2):
    intersection = np.logical_and(image1, image2)  # 获取两个图像的交集
    return np.sum(intersection)  # 计算交集中白色像素的数量，即公共白色区域的面积

def distance(loc1,loc2):
    return ((loc2[0]-loc1[0])**2+(loc2[1]-loc1[1])**2)**0.5

def curve_length(x, y):
    dx = np.diff(x)
    dy = np.diff(y)
    ds = np.sqrt(dx**2 + dy**2)
    return np.sum(ds)

def nearest_pixel(binary_image, start_point):
    rows, cols = len(binary_image), len(binary_image[0])
    visited = set()
    queue = deque([start_point])
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    while queue:
        row, col = queue.popleft()
        if binary_image[col][row] == 255:
            return (row, col)

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return None

def draw_ploy(img,x,y,color = (255,255,255)):
    # 创建一个空白的图像作为掩模
    pts = np.array([x, y], np.int32)
    pts = pts.T.reshape((-1, 1, 2))
    cv2.fillPoly(img, [pts], color=color)  # 用黑色填充多边形
    ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return binary

def max_radius(a, b, x, y):
    keypoint = b
    img = np.zeros((3072, 4096), dtype=np.uint8)
    img.fill(0)  # 填充为白色
    binary = draw_ploy(img,x,y)
    all_s_com_rs = 0
    radius = 50
    for i in range(10,100,2):
        rs = 2*np.pi*i
        test_image = draw_circle(img,keypoint,i,'white')
        all_s = white_intersection_area(test_image,binary)
        new_all_s_com_rs = all_s/rs
        if new_all_s_com_rs>=all_s_com_rs:
            all_s_com_rs = new_all_s_com_rs
            radius = i
        else:
            break
    return radius

def overlap_area_circle_polygon(center_x, center_y, radius, polygon_x, polygon_y):
    # 创建圆形对象
    circle = Point(center_x, center_y).buffer(radius)
    # 创建多边形对象
    polygon_points = list(zip(polygon_x, polygon_y))
    polygon = Polygon(polygon_points)
    # 计算重叠区域
    overlap_polygon = circle.intersection(polygon)
    # 计算重叠面积
    overlap_area = overlap_polygon.area
    return overlap_area

def count_lattice_points_in_circle(r):
    count = 0
    for x in range(r):
        for y in range(r):
            if x*x + y*y <= r*r or (x+1)*(x+1) + (y+1)*(y+1) <= r*r:
                count += 1
    return count

def convert_to_images(data):
    images = []
    for i in range(data.shape[0]):
        image = data[i].type(torch.uint8) * 255  # 将True变为255，False变为0
        image = image.numpy()  # 转换为NumPy数组
        # image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # 转换为BGR格式
        images.append(image)
    return images

def re_ploy(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    largest_contour = max(contours, key=cv2.contourArea)  # 只保留面积最大的轮廓
    contours = [largest_contour]
    points = []
    for index, contour in enumerate(contours):
        epsilon_factor = 0.001
        epsilon = epsilon_factor * cv2.arcLength(contour, True)
        contour = cv2.approxPolyDP(contour, epsilon, True)
        if len(contour) < 3:
            continue
        for point in contour:
            x, y = point[0]
            points.append([x, y])
    x = []
    y = []
    for i in range(len(points)):
        x.append(points[i][0])
        y.append(points[i][1])
    odd_list = np.array(x)
    even_list = np.array(y)
    return odd_list,even_list

def delta_distance(point,image):
    image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    if image[point[1]][point[0]] == 255:
        rate = -1
    else:
        rate = 1
    r = 3
    w, h = image.shape
    while True:
        circle_mask = np.zeros((w, h), dtype=np.uint8)
        cv2.circle(circle_mask, point, r, 255, -1)
        overlap_mask = cv2.bitwise_and(image, circle_mask)
        overlap_area = np.sum(overlap_mask == 255)
        if overlap_area>math.pi*r**2*0.95 or overlap_area<math.pi*r**2*0.05:
            break
        else:
            r+=2
    # print(r)
    if rate==-1:
        image = cv2.bitwise_not(image)
    point1 = nearest_pixel(image,point)
    return rate*r,point1
def calculate_length(a, b, x, y,radius):
    """
    a:keypoint direction
    b:keypoint direction
    x,y:odd list and even list of mask boundary coordinates
    radius:Inflation search algorithm search radius
    """
    # 确定线束可能搜索的区域
    min_x,max_x = min(min(x),a[0],b[0])-radius,max(max(x),a[0],b[0])+radius
    min_y,max_y = min(min(y),a[1],b[1])-radius,max(max(y),a[1],b[1])+radius
    dx = int(max_x-min_x)
    dy = int(max_y-min_y)
    # 坐标转换
    x = [xx-min_x for xx in x]
    y = [yy-min_y for yy in y]
    keypoint2 = [a[0]-min_x,a[1]-min_y]
    keypoint1 = [b[0]-min_x,b[1]-min_y]
    # 绘制多边形
    img = np.zeros((dy, dx), dtype=np.uint8)
    img.fill(0)  # 填充为白色
    binary = draw_ploy(img,x,y)
    # 对搜索半径和多边形的粗细进行微调，避免搜索路径过短，产生较大的误差
    radius = int(radius)
    # if radius>30:
    #     kernel = np.ones(((radius-30)//2, (radius-30)//2), np.uint8)
    #     radius = 20
    #     binary = cv2.erode(binary, kernel)
    directions = min(count_lattice_points_in_circle(radius),30)
    # print(f'搜索方向数{directions},搜索半径{radius},起始点和终点{a,b}')
    route = [keypoint1]
    image = copy.deepcopy(binary)
    dist = distance(route[-1],keypoint2)
    image = draw_circle(image, (route[0][0], route[0][1]), radius, 'white')
    # 膨胀搜索
    while dist>radius:
        last_x,last_y = route[-1]
        centers = [[last_x+radius*(math.cos(j*2*np.pi/directions)),last_y+radius*math.sin(j*2*np.pi/directions)] for j in range(directions)]
        areas = []
        centers = [list(map(int, c)) for c in centers]
        for j in range(directions):
            # 计算搜索区域与掩码重叠的面积
            center = centers[j]
            circle_mask = np.zeros((dy,dx), dtype=np.uint8)
            cv2.circle(circle_mask, center, radius, 255, -1)
            overlap_mask = cv2.bitwise_and(image, circle_mask)
            overlap_area = np.sum(overlap_mask == 255)
            areas.append(overlap_area)
        image = draw_circle(image,(last_x,last_y),radius,'black')
        loc = centers[areas.index(max(areas))]
        route.append(loc)
        dist = distance(route[-1], keypoint2)
        if max(areas)<radius//5:
            break
    route.append(keypoint2)
    # print(route)
    x_list, y_list = zip(*route)
    if len(x_list)<=4:
        return False
    # 将搜索路径拟合曲线
    tck, u = splprep([x_list, y_list], s=50)
    new_points = splev(np.linspace(0, 1, 1000), tck)
    # 计算曲线长度
    length = curve_length(new_points[0],new_points[1])
    # if length>900:
    x_coords, y_coords = new_points
    binary = cv2.cvtColor(binary,cv2.COLOR_GRAY2RGB)
    for i in range(1, len(x_coords)):
        cv2.line(binary, (int(x_coords[i - 1]), int(y_coords[i - 1])), (int(x_coords[i]), int(y_coords[i])), (255, 0, 0),1)
    # Img = cv2.resize(binary, None, fx=2, fy=2)
    # cv2.imshow('Line Plot', binary)
    # cv2.waitKey(0)  # 等待用户按键
    return length

def Inflation_search(a, b, Img, radius,ppp=0):
    """
    a:keypoint direction
    b:keypoint direction
    x,y:odd list and even list of mask boundary coordinates
    radius:Inflation search algorithm search radius
    """
    keypoint2 = [int(a[0]),int(a[1])]
    keypoint1 = [int(b[0]),int(b[1])]
    # delta1,keypoint1 = delta_distance(keypoint1,Img)
    # delta2,keypoint2 = delta_distance(keypoint2,Img)
    # delta = delta1+delta2
    route = [keypoint1]
    img = cv2.cvtColor(Img, cv2.COLOR_RGB2GRAY)
    _, binary_image = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    # inverted_image = cv2.bitwise_not(binary_image)
    dist = distance(route[-1],keypoint2)
    image = draw_circle(binary_image, (route[0][0], route[0][1]), radius, 'white')
    # 膨胀搜索
    w,h = image.shape
    while dist>radius*2:
        last_x,last_y = route[-1]
        directions = min(count_lattice_points_in_circle(radius), 128)
        # print(directions)
        centers = [[last_x+radius*(math.cos(j*2*np.pi/directions)),last_y+radius*math.sin(j*2*np.pi/directions)] for j in range(directions)]
        centers = [list(map(int, c)) for c in centers]
        searched = 0
        excessive = False
        while True:
            areas = []
            for j in range(directions):
                # 计算搜索区域与掩码重叠的面积
                center = centers[j]
                circle_mask = np.zeros((w,h), dtype=np.uint8)
                cv2.circle(circle_mask, center, radius, 255, -1)
                overlap_mask = cv2.bitwise_and(image, circle_mask)
                overlap_area = np.sum(overlap_mask == 255)
                areas.append(overlap_area)
            area = math.pi*radius**2
            if excessive:
                if max(areas)>area*0.05:
                    break
                else:
                    radius = max(int(radius*2),3)
                    if radius>w:
                        break
            elif max(areas)<area*0.65:
                searched+=1
                # if searched == 2:
                #     radius = int(radius*2.5)
                #     continue
                if searched>3:
                    excessive = True
                    continue
                radius=max(int(radius*0.9),3)
                # print('半径缩小')
                # print(areas)
            elif max(areas)>area*0.75:
                radius=max(int(radius*1.25),radius+1)
                # print('半径扩大')
                # print(areas)
            else:
                break
        image = draw_circle(image,(last_x,last_y),radius,'black')# 矩形覆盖
        loc = centers[areas.index(max(areas))]
        route.append(loc)
        dist = distance(route[-1], keypoint2)
        if max(areas)<radius//5:
            break
    route.append(keypoint2)
    # print(route)
    x_list, y_list = zip(*route)
    if len(x_list)<=3:
        return False,None
    # 将搜索路径拟合曲线
    tck, u = splprep([x_list, y_list])
    new_points = splev(np.linspace(0, 1, 1000), tck)
    # 计算曲线长度
    length = curve_length(new_points[0],new_points[1])
    x_coords,y_coords = new_points
    for i in range(1, len(x_coords)):
        cv2.line(Img, (int(x_coords[i - 1]), int(y_coords[i - 1])), (int(x_coords[i]), int(y_coords[i])), (0,0,255), 1)
    for i in range(1, len(x_list)):
        cv2.line(Img, (int(x_list[i - 1]), int(y_list[i - 1])), (int(x_list[i]), int(y_list[i])), (0,255,0), 1)
    Img = cv2.resize(Img,None,fx=2,fy=2)
    cv2.imshow('Line Plot', Img)
    cv2.waitKey(0)  # 等待用户按键
    return length,Img
