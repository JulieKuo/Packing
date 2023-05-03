from utils import *
from plot import *
import shutil, json, sys, base64
from log_config import Log
from traceback import format_exc

log = Log()
logging = log.set_log(name = "run")


def main(param):
    try:
        logging.info(f"Input - {param}")

        # 初始化存放圖片的資料夾
        root = param["root"]
        folder = os.path.join(root, "data", "image")
        if os.path.exists(folder):
            shutil.rmtree(folder) # 刪除資料夾

        # 棧板大小、總高、機器手臂空隙設定
        plate = [param["plate"][0], param["plate"][1], param["plate"][2]]
        z_limit = param["total_height"]
        gap = param["gap"]

        # 兩種排序方式: 長邊橫著牌或直著排
        options = [
            [param["item"][1], param["item"][2], param["item"][0]],
            [param["item"][0], param["item"][2], param["item"][1]]
            ]
        if param["item"][0] == param["item"][1]: # 如果長寬一樣，只有一種排法
            options.pop()

        # 依序計算不同擺放方式所能放入的總立方體數及位置
        datas = {}
        for option in options: 
            # 設定立方體的擺放方式
            length = option[0]
            width = option[1]
            hight = option[2]
            length_gap = length + gap # 長加上機器手臂的距離

            # 計算各層各圈各區域的立方體的座標及移動位置
            items = {}
            counts_info = {}
            layers = (z_limit - plate[2]) // hight # 計算共可疊幾層
            for layer in range(layers):
                # print(f"layer{layer}:")
                items[f"layer{layer}"] = {}
                
                start = [0, 0, (plate[2] + hight * layer)]# 各層的高須先加上棧板高度
                limit = [plate[0], plate[1], z_limit]

                laps = min(int(limit[0] // (length_gap * 2) + 1), int(limit[1] // (length_gap * 2) + 1)) # 計算該層共可放幾圈
                for lap in range(laps):
                    # print(f"-> lap{lap}:")
                    items[f"layer{layer}"][f"lap{lap}"] = {}

                    even = (layer % 2 == 0) # True: 第0、2、4...層；False:第1、3、5...層
                    x_count, y_count, counts = calculate_counts(start, limit, length_gap, width, even) # 計算該層該圈的各區域立方體數量

                    # 記錄各層x、y軸擺放的立方體數量
                    if layer == 0:
                        counts_info[f"lap{lap}"] = {"x_count": x_count, "y_count": y_count}

                    # 刪除剩餘空間，即所有立方體往原點靠近，空隙往右上移
                    # if (lap == 0):
                    limit[0] = start[0] + (x_count * width) + (length_gap * (y_count != 0))
                    limit[1] = start[1] + (y_count * width) + (length_gap * (x_count != 0))

                    points = set_points(start, limit) # 初始化各區域立方體座標

                    for area in range(4):
                        # print(f"--> area{area}")
                        items[f"layer{layer}"][f"lap{lap}"][f"area{area}"] = []
                        for _ in range(int(counts[area])):
                            cube, points = add_item(area, points, length, width, hight, even) # 新增立方體
                            items[f"layer{layer}"][f"lap{lap}"][f"area{area}"].append(cube) # 保存立方體資訊
                            
                            cube["info"] = f"第{layer + 1}層_第{area + 1}區_第{lap + 1}圈"

                    start, limit = update_start_limit(start, limit, length, gap) # 更新下一圈的start和limit座標

            # 排序立方體，並將其放入list中以畫圖
            total_items = sort_items(plate, items)

            counts = len(total_items) - 1
            logging.info(f"Product - length: {length}, width: {width}, hight: {hight}, counts = {counts}")

            size = [length, width, hight]
            datas[hight] = {
                "size": size,
                "counts": counts,
                "layer": layers,
                "laps": laps,
                "total_hight": hight * (layer + 1) + plate[2], # 加棧板總高
                "layer_counts": int(counts / 2), # 每層有幾個
                "counts_info": counts_info, # 各圈x、y軸排法
                "data": items,
                "sort": total_items
            }

            if counts != 0:
                # 創建儲存圖片的資料夾
                image_folder_path = os.path.join(root, "data", "image", str(hight))
                os.makedirs(image_folder_path) 

                # 依序畫出各步驟的圖
                for i in range(1, len(total_items) + 1):
                    plot(total_items[:i], plate, size, gap, z_limit, image_folder_path)
                
                # 將圖片轉為影片
                images_to_vedio(root, image_folder_path, param, hight, gap)
            
        # 儲存datas
        with open(os.path.join(root, "data", "data.json"), 'w') as f:
            json.dump(datas, f, indent = 4)
    

    except:
        logging.error(format_exc())


    finally:
        logging.info("-" * 100)
        log.shutdown()



if __name__ == "__main__":
    if len(sys.argv) > 1:
        # param = eyJwbGF0ZSI6IFsxMTEwLCA5NTAsIDEwMF0sICJpdGVtIjogWzYwMCwgMTQwLCA5MF0sICJ0b3RhbF9oZWlnaHQiOiAxMzE1LCAiZ2FwIjogMjUsICJyb290IjogIkM6XFxVc2Vyc1xcdHp1bGlcXERvY3VtZW50c1xccHl0aG9uXFxQYWNraW5nIn0=
        param = sys.argv[1]
        param = base64.b64decode(param).decode('utf-8')
        param = json.loads(param)

        main(param)

    else:
        print("The input parameter is wrong.")
    
