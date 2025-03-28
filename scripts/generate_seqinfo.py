import os
import json


def create_seqinfo(json_file, base_folder):
    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    # 遍历 JSON 数据
    for item in data:
        file_name = item["file_name"]
        width = item["width"]
        height = item["height"]
        length = item["length"]

        # 构造目标文件夹路径
        target_folder = os.path.join(base_folder, file_name)

        # 检查目标文件夹是否存在
        if os.path.isdir(target_folder):
            seqinfo_path = os.path.join(target_folder, "seqinfo.ini")

            # 构造 seqinfo.ini 文件内容
            seqinfo_content = f"""[Sequence]
name={file_name}
seqLength={length}
imWidth={width}
imHeight={height}
imExt=.png
"""

            # 写入 seqinfo.ini 文件
            with open(seqinfo_path, "w", encoding='utf-8') as seq_file:
                seq_file.write(seqinfo_content)
            print(f"Created: {seqinfo_path}")
            count = count + 1
        else:
            print(f"Folder not found: {target_folder}")
    print(f"Created {count} sequences")


# 示例调用
json_path = "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/video_info_valid.json"  # 你的 JSON 文件路径
folder_path = "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/temporal/OVIS/val"  # 你的文件夹路径
create_seqinfo(json_path, folder_path)
