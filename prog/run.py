from util import *
from tool import *
from plot import *
import shutil, json
from log_config import Log
from traceback import format_exc



class Main():
    def __init__(self, root: str) -> None:
        self.root = root
        self.activate_log() # activate log setting


    def basic(self):
        self.get_input() # get input parameters

        # 初始化存放圖片的資料夾
        data_folder = os.path.join(self.root, "data")
        self.image_folder = os.path.join(data_folder, "image")
        if os.path.exists(self.image_folder):
            shutil.rmtree(self.image_folder) # 刪除資料夾

        self.vedio_folder = os.path.join(data_folder, "vedio")
        self.output_json  = os.path.join(data_folder, "output.json")
        self.data_json    = os.path.join(data_folder, "data.json")
    

    def activate_log(self):
        # initialize log
        self.log = Log()

        # create log folder
        log_path = os.path.join(self.root, "logs")
        os.makedirs(log_path, exist_ok = True)

        # set log
        self.logging = self.log.set_log(filepath = os.path.join(log_path, "log.log"), level = 2, freq = "D", interval = 50, backup = 3, name = "log")

        self.logging.info("-" * 200)


    def get_input(self):
        self.input = get_argv(self.logging)
        self.time = self.input["time"]


    def run(self):
        try:            
            self.basic() # basic setting

            # 棧板大小、總高、機器手臂空隙設定
            plate = [self.input["plate"][0], self.input["plate"][1], self.input["plate"][2]]
            z_limit = self.input["total_height"]
            gap = self.input["gap"]

            # 兩種排序方式: 長邊橫著排或直著排
            options = [
                [self.input["item"][1], self.input["item"][2], self.input["item"][0]], # 直放
                [self.input["item"][0], self.input["item"][2], self.input["item"][1]]  # 橫放
                ]
            if self.input["item"][0] == self.input["item"][1]: # 如果長寬一樣，只有一種排法
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
                items = {} # 儲存每層每圈每區的資料
                counts_info = {} # 每圈x軸和y軸上的箱子數
                layers = (z_limit - plate[2]) // hight # 計算共可疊幾層
                for layer in range(layers):
                    # print(f"layer{layer}:")
                    items[f"layer{layer}"] = {}
                    
                    start = [0, 0, (plate[2] + hight * layer)]# 各層的起始高須先加上棧板高度
                    limit = [plate[0], plate[1], z_limit]
                    
                    # 計算共可放幾圈
                    # 每圈至少要大於兩個length_gap (1 & 3區、2 & 4區)
                    # 加1代表剩下的空間，可另外進行排序
                    laps = min(int(limit[0] // (length_gap * 2) + 1), int(limit[1] // (length_gap * 2) + 1))
                    
                    for lap in range(laps):
                        # print(f"-> lap{lap}:")
                        items[f"layer{layer}"][f"lap{lap}"] = {}

                        even = (layer % 2 == 0) # True: 第0、2、4...層；False:第1、3、5...層
                        x_count, y_count, counts = calculate_counts(start, limit, length_gap, width, even) # 計算該層該圈的各區域立方體數量

                        # 記錄各層x、y軸擺放的立方體數量
                        if layer == 0:
                            counts_info[f"lap{lap}"] = {"x_count": x_count, "y_count": y_count}

                        # 刪除剩餘空間，即所有立方體往原點靠近，空隙往右上移
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
                self.logging.info(f"Product - length: {length}, width: {width}, hight: {hight}, counts = {counts}")

                size = [length, width, hight]
                datas[hight] = {
                    "size": size,
                    "counts": counts,
                    "layer": layers,
                    "laps": laps,
                    "total_height": hight * (layer + 1) + plate[2], # 加棧板總高
                    "layer_counts": int(counts / 2), # 每層有幾個
                    "counts_info": counts_info, # 各圈x、y軸排法
                    "data": items,
                    "sort": total_items
                }

                if counts != 0:
                    # 創建儲存圖片的資料夾
                    image_folder1 = os.path.join(self.image_folder, str(hight))
                    os.makedirs(image_folder1) 

                    # 依序畫出各步驟的圖
                    for i in range(1, len(total_items) + 1):
                        plot(total_items[:i], plate, size, gap, z_limit, image_folder1)
                    
                    # 將圖片轉為影片
                    images_to_vedio(self.vedio_folder, image_folder1, self.input, hight, gap)
                
            # 儲存datas
            with open(file = self.data_json, mode = "w", encoding = 'utf-8') as file:
                json.dump(datas, file, indent = 4, ensure_ascii = False)


            result = {
                "status": "success",
                "time":   self.time
                }
                    

        except:
            message = format_exc()
            result  = error(self.logging, message, self.time)


        finally:            
            self.logging.info(f'Save output to {self.output_json}')
            with open(file = self.output_json, mode = "w", encoding = 'utf-8') as file:
                json.dump(result, file, indent = 4, ensure_ascii = False)
            self.log.shutdown()



if __name__ == "__main__":
    # Get root directory
    file_path = os.path.abspath(__file__)
    prog_path = os.path.dirname(file_path)
    root = os.path.dirname(prog_path)

    main = Main(root)
    main.run()