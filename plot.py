import cv2, os, glob
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']


def plot(items, plate, size, gap, z_limit, path):
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d') # 此ax為1x1網格中的第一個子圖，此圖為3D圖
    ax.view_init(elev = 90, azim = -90) # 調整視角

    for num, item in enumerate(items):
        # 定義立方體的八個頂點
        vertices = np.array([
            [item["x"]             , item["y"]             , item["z"]             ], # point0
            [item["x"] + item["dx"], item["y"]             , item["z"]             ], # point1
            [item["x"] + item["dx"], item["y"] + item["dy"], item["z"]             ], # point2
            [item["x"]             , item["y"] + item["dy"], item["z"]             ], # point3
            [item["x"]             , item["y"]             , item["z"] + item["dz"]], # point4
            [item["x"] + item["dx"], item["y"]             , item["z"] + item["dz"]], # point5
            [item["x"] + item["dx"], item["y"] + item["dy"], item["z"] + item["dz"]], # point6
            [item["x"]             , item["y"] + item["dy"], item["z"] + item["dz"]], # point7
            ])

        # 定義立方體的所有邊
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0], # 底邊
            [4, 5], [5, 6], [6, 7], [7, 4], # 頂邊
            [0, 4], [1, 5], [2, 6], [3, 7], # 四邊
            ]
        
        # 定義立方體的六個面
        faces = np.array([
            [0, 1, 2, 3], # 底面
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7], # 頂面
                        ])

        # 建立 Line3DCollection 物件，設置顏色和線條寬度
        lines = Line3DCollection([vertices[edge] for edge in edges], colors = 'black', linewidths = 0.5, alpha = 0.15)

        # 建立 Poly3DCollection 物件，設置顏色和透明度
        if num == 0: # 棧板顏色
            color = "#994D4D"
        elif num == len(items) - 1: # 新增的立方體設定藍色
            color = ["#D2E9FF", "#C4E1FF", "#C4E1FF", "#C4E1FF", "#C4E1FF", "#D2E9FF"] # 新的立方體
        else:
            color = ["#F4FFFF", "#EBFFFF", "#EBFFFF", "#EBFFFF", "#EBFFFF", "#F4FFFF"] # 舊的立方體
        

        cube = Poly3DCollection([vertices[faces[i]] for i in range(len(faces))], alpha = 0.8, facecolor = color)

        # 添加 Poly3DCollection 物件到坐標軸
        ax.add_collection3d(cube)
        ax.add_collection3d(lines) 

    # 在頂面添加文字描述
    ax.text(
        x = item["x"] + item["dx"]/2,
        y = item["y"] + item["dy"]/2,
        z = item["z"] + item["dz"],
        s = str(num), fontsize = 16, color = 'black', ha = 'center', va = 'center', alpha = 1, zorder = np.inf
        )

    # 設定標題和副標題
    ax.set_title(
        f'''棧板: {plate[0]}x{plate[1]}x{plate[2]},  箱子: {size[0]}x{size[1]}x{size[2]},  空隙: {gap}\n'''
        , fontsize = 20, color = 'black', ha = 'center', va = 'center'
        )
    
    # 添加解釋文字
    fig.text(
        x = 0.5, # 水平位置為圖片寬度的一半
        y = 0.1, # 垂直位置為圖片下方 5% 的位置
        s = f'''No. {num}
{item["info"]}
(x, y, z) = ({item["x"]}, {item["y"]}, {item["z"]})
(dx, dy, dz) = ({item["dx"]}, {item["dy"]}, {item["dz"]})''', # 解釋文字
        fontsize = 18, color = 'black', ha = 'center', va = 'center'
    )

    # 設置坐標軸範圍和標籤
    ax.set_xlim(0, plate[0])
    ax.set_ylim(0, plate[1])
    ax.set_zlim(0, z_limit)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    ax.set_zticks([]) # z軸不顯示刻度

    # 設定坐標軸的比例，使其看起來更拉長
    ax.set_box_aspect([1, 1, 1])
    
    # 儲存圖片
    plt.savefig(f"{path}/{num}.png")

    # 顯示圖形
    # plt.show()
    
    plt.close()


def images_to_vedio(root, image_folder_path, param, hight, gap):
    # 設定輸出影片路徑
    folder_name = "_".join(str(i) for i in param["item"])
    folder_path = os.path.join(root, f"data\\vedio\\{folder_name}")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    output_path = os.path.join(folder_path, f"{hight}_{gap}.mp4")

    # 取得資料夾中所有的png檔案名稱，依照創建日期排序
    file_names = sorted(glob.glob(os.path.join(image_folder_path, "*.png")), key = os.path.getctime)

    # 讀取第一張圖片，並取得圖片大小
    first_frame = cv2.imread(file_names[0])
    frame_height, frame_width, _ = first_frame.shape

    # 設定影片編碼器和fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 5

    # 建立影片寫入器
    video_writer = cv2.VideoWriter(filename = output_path, fourcc = fourcc, fps = fps, frameSize = (frame_width, frame_height))

    # 讀取每張圖片，並將圖片加入影片寫入器
    for file_name in file_names:
        img = cv2.imread(file_name) 
        video_writer.write(img)

    # 釋放影片寫入器
    video_writer.release()