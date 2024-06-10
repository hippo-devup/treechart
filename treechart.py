import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, PathPatch
from matplotlib.path import Path
from matplotlib.animation import FuncAnimation

import numpy as np

from collections import defaultdict
import pandas as pd

from datetime import datetime
import random

import time, os

# 更新字体设置以支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示

# 模拟更多数据
dates  = []
events = []
attributes = []

# 加载Excel文件
df = pd.read_excel(r'diary.xlsx', header=None)

for idx, row in df.iterrows():
	index = idx 
	date = str(df.iloc[index, 1])
	print(str(df.iloc[index, 0]))
	
	date = date.replace('上', '.5').replace('中', '.15').replace('下', '.25')
	if date.count('.') == 1:
		date += '.15'
	elif date.count('.') == 0:
		date += '6.15'
	

	if str(df.iloc[index, 0]).strip() != 'nan':
		dates.append(datetime.strptime(date, "%Y.%m.%d"))
		events.append(df.iloc[index, 0])
		attributes.append(0)

	if str(df.iloc[index, 2]).strip() != 'nan':
		dates.append(datetime.strptime(date, "%Y.%m.%d"))
		events.append(df.iloc[index, 2])
		attributes.append(1)

for i in range(0, len(dates)):
	print(dates[i], events[i], attributes[i])
	
data = {
	"日期": dates,
	"事件": events,
	"属性": attributes
}

df_simulated = pd.DataFrame(data)
df_simulated['日期'] = pd.to_datetime(df_simulated['日期'])
df_simulated.sort_values('日期', inplace=True, ignore_index=True)


# 创建图形和轴
fig, ax = plt.subplots(figsize=(12, 18))  # 大尺寸图形

# 绘制树干
trunk_x = [0.5, 0.5]
trunk_y = [0, 1]
ax.plot(trunk_x, trunk_y, color='brown', linewidth=48, zorder=1)

# 为每个日期和类型计算树叶的位置
date_type_positions = defaultdict(list)
enumrated = []
for index, row in df_simulated.iterrows():
	date_type_positions[(row['日期'], row['属性'])].append(index)
	enumrated.append((row['日期'], row['属性'], index))
	
# 假设 df_simulated 已经包含了日期和事件类型的数据
# 首先找到最早和最晚的日期
min_date = df_simulated['日期'].min()
max_date = df_simulated['日期'].max()

# 定义一个函数，根据日期计算垂直位置
def date_to_y_coord(date, min_date, max_date):
    return 0.05 + 0.8 * ((date - min_date) / (max_date - min_date))

left_y = 0
right_y = 0	
left_x = 0
right_x = 0
# 添加树叶
saved_date = ''
path = os.getcwd()

def init():
    pass
	
def update(frame, init_called=[False]):
	global left_y, right_y, right_x, left_x, saved_date
	
	if frame == 0 and not init_called[0]:
		init_called[0] = True  # 初始化调用时设置标志
		
	date, attr, df_simulated_idx = enumrated[frame]
	#indexes = date_type_positions[(date, attr)]
	
	base_y = date_to_y_coord(date, min_date, max_date)  # 使用日期计算垂直位置
	
	y_acc = base_y - 0.04
	#for i, df_simulated_idx in enumerate(indexes):
	
	# 根据属性选择左边或右边
	randomdiff = random.randint(-2, 2)
	x  = 0.3 if attr == 0 else 0.7
	x += 0.025 * randomdiff
	
	if left_x  > x + 0.05:# 垂直偏移
		y_acc += 0.01 
	else:
		y_acc += 0.03

	y = y_acc + 0.05
		
	if attr == 0:
		if y < left_y + 0.02:
			y = left_y + 0.02
			
		left_y = y
		left_x = x
	else:
		if y < right_y + 0.03:
			y = right_y + 0.03

		right_y = y
		right_x = x
		
	if saved_date != date.strftime('%Y'):
		ax.text(0.485, base_y - 0.02, date.strftime('%Y'), verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
		
	text_content = f" {df_simulated.iloc[df_simulated_idx]['日期'].strftime('%m-%d')} {df_simulated.iloc[df_simulated_idx]['事件']} "
	saved_date = date.strftime('%Y')
	
	linearray = ['xkcd:green', 'xkcd:light green', 'xkcd:lime green', 'xkcd:grass green', 'xkcd:salmon', 'xkcd:orange', 'xkcd:peach', 'xkcd:light orange']
	color = linearray[attr * 4 + random.randint(0, 3)]
	# 椭圆大小调整以包裹文本
	
	text_size = ax.text(0, 0, text_content, fontsize=10, va='center', ha='center')
	bbox = text_size.get_window_extent(renderer=fig.canvas.get_renderer())
	text_size.remove()
	
	leaf_width = bbox.width / fig.dpi / fig.get_size_inches()[0] + 0.05  # 将像素宽度转换为坐标宽度并添加一些边距
	leaf_height = bbox.height / fig.dpi / fig.get_size_inches()[1] + 0.03  # 将像素高度转换为坐标高度并添加一些边距
	
	leaf = Ellipse((x, y), width=leaf_width, height=leaf_height, angle=0, color=color, zorder=2)
	ax.add_patch(leaf)
	
	# 绘制曲线连接到树干
	verts = [(x + leaf_width / 4, y), (x + leaf_width / 4, y - 0.02), (0.5, base_y - 0.02), (0.5, base_y)]
	codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
	path = Path(verts, codes)
	patch = PathPatch(path, facecolor='none', lw=1, edgecolor=color)
	ax.add_patch(patch)
	
	ax.text(x, y, text_content, va='center', ha='center', fontsize=10, zorder=3)
	ax.plot(trunk_x, trunk_y, color='brown', linewidth=48, zorder=1)
	
	if frame == len(df_simulated) - 1:
		plt.savefig(os.path.join(path, 'Event_Tree_Visualization.png'), format='png', dpi=300)

# 设置图形属性
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')  # 隐藏轴

ani = FuncAnimation(fig, update, frames=len(df_simulated), repeat=False, interval=500, init_func=init)

#ani.save(os.path.join(path, 'my_animation.mp4'), writer='ffmpeg', fps=2)
plt.show()