def set_position(point, dx, dy, dz):
    # 立方體座標，及移至左上角所需移動的量
    position = {
        "x": point[0], 
        "y": point[1], 
        "z": point[2],
        "dx": dx, 
        "dy": dy, 
        "dz": dz
    }

    return position


def calculate_counts(start, limit, length, width, even):
    x_range = limit[0] - start[0] # x軸可放立方體的空間
    y_range = limit[1] - start[1] # y軸可放立方體的空間

    total = 0
    flag = 1

    if ((length + width) <= x_range) and ((length + width) <= y_range): # 確認4個area至少都可以放下一個立方體
        x_count = (x_range - length) // width # 沿著x軸方向排列之立方體數量
        y_count = (y_range - length) // width # 沿著y軸方向排列之立方體數量

        while ((x_count * width) > ((length + (x_count * width)) / 2)) and ((y_count * width) < ((length + (y_count * width)) / 2)): # 處理重疊的部分 # 內層刪除多餘空間
            x_count -= 1
        
        total = (x_count * 2) + (y_count * 2)
    else:
        x_count = y_count = 0
        counts = [0, 0, 0, 0]
    
    # 無法排四個區域，但可集中放在一個區域，即全部橫排(沿x軸排)或直排(沿y軸排)便可放入
    if (length <= y_range): # 橫排(沿x軸排)
        x_count1 = x_range // width # 沿著x軸方向排列之立方體數量
        if x_count1 > total:
            x_count = total = x_count1
            y_count = flag = 0
    if (length <= x_range): # 直排(沿y軸排)
        y_count1 = y_range // width # 沿著y軸方向排列之立方體數量
        if y_count1 > total:
            y_count = total = y_count1
            x_count = flag = 0
    
    if even:
        counts = [(y_count * flag), (x_count * flag), y_count, x_count] # 若集中放在一個區域，4個值裡只有1個值不為0
    else:
        counts = [(x_count * flag), (y_count * flag), x_count, y_count]
    
    return x_count, y_count, counts


def add_item(area, points, length, width, catch, even):
    if even: # 雙數層
        if area == 0:
            cube = set_position(point = points[0], dx = length, dy = width, dz = catch) # 將立方體資訊儲存在dict中
            points[0][1] += width # 更新該區域立方體座標
        elif area == 1:
            cube = set_position(point = points[1], dx = -width, dy = length, dz = catch)
            points[1][0] -= width
        elif area == 2:
            cube = set_position(point = points[2], dx = -length, dy = -width, dz = catch)
            points[2][1] -= width
        else:
            cube = set_position(point = points[3], dx = width, dy = -length, dz = catch)
            points[3][0] += width
    else: # 單數層轉向排序
        if area == 0:
            cube = set_position(point = points[0], dx = width, dy = length, dz = catch)
            points[0][0] += width
        elif area == 1:
            cube = set_position(point = points[1], dx = -length, dy = width, dz = catch)
            points[1][1] += width
        elif area == 2:
            cube = set_position(point = points[2], dx = -width, dy = -length, dz = catch)
            points[2][0] -= width
        else:
            cube = set_position(point = points[3], dx = length, dy = -width, dz = catch)
            points[3][1] -= width
    
    return cube, points


def set_points(start, limit):
    point0 = [start[0], start[1], start[2]]
    point1 = [limit[0], start[1], start[2]]
    point2 = [limit[0], limit[1], start[2]]
    point3 = [start[0], limit[1], start[2]]

    points = [point0, point1, point2, point3]

    return points


def update_start_limit(start, limit, length, gap):
    start = [start[0] + (length + gap), start[1] + (length + gap), start[2]] # 更新點0
    limit = [limit[0] - (length - gap), limit[1] - (length - gap), start[2]] # 更新點2

    return start, limit


def sort_items(plate, items):
    total_items = []

    # 新增棧板位置
    total_items.append({"x": 0, "y": 0, "z": 0, "dx": plate[0], "dy": plate[1], "dz": plate[2], "info": "棧板"})

    # 新增立方體
    for layer_name, layer in items.items():
        # 判斷單數層或雙數層，給予對應的排序區域。由外而內(原點)排序區域。
        areas = ["area3", "area2", "area1", "area0"] if (int(layer_name[5:]) % 2) == 0 else ["area2", "area1", "area3", "area0"]
        for i, area_name in enumerate(areas):
            if i >= 2:
                layer = dict(sorted(layer.items(), key = lambda x: x[0], reverse = True)) # 靠近原點的區域從內圈開始往外排，才能由外而內(原點)排序

            # 雙數層第0區和單數層第0、1區的順序與一開始存的不同，需轉向
            for lap in layer.values():
                if (((int(layer_name[5:]) % 2) == 0) and (area_name in ["area0"])) or\
                   (((int(layer_name[5:]) % 2) != 0) and (area_name in ["area1", "area0"])):
                    total_items.extend(lap[area_name][::-1]) # 倒序才能由外而內(原點)排序立方體
                else:
                    total_items.extend(lap[area_name])
    
    return total_items