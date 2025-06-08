import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use("TKAgg")

# 设置中文字体（windows下常用SimHei）
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

labels = ['Precision', 'Recall', 'F1 Score']

before = [0.7139, 0.7352, 0.722]
after = [0.8173, 0.7397, 0.7756]

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor('#f7f7f7')  # 设置整体背景颜色为浅灰

# 定义颜色和透明度
color_before = '#4c72b0'  # 蓝色系
color_after = '#55a868'   # 绿色系

rects1 = ax.bar(x - width/2, before, width, label='微调前', color=color_before, alpha=0.85, edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x + width/2, after, width, label='微调后', color=color_after, alpha=0.85, edgecolor='black', linewidth=0.8)

ax.set_ylabel('得分', fontsize=14, fontweight='bold')
ax.set_title('微调前后评价指标对比', fontsize=18, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=13)
ax.set_ylim(0, 1)

# 添加网格线，方便对比
ax.grid(axis='y', linestyle='--', alpha=0.7)

# 数值标签，字体调整
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=11,
                    fontweight='bold',
                    color='black')

autolabel(rects1)
autolabel(rects2)

# 图例字体大小
ax.legend(fontsize=13)
plt.tight_layout()
plt.show()
