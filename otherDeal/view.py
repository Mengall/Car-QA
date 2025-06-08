import faiss
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use("TKAgg")

# 读取 index
index = faiss.read_index(r"D:\PythonWeb\Car_QuestionSystem\data\object_car_vectors_ip.index")
ntotal = index.ntotal
d = index.d

# 提取所有向量
xb = np.vstack([index.reconstruct(i) for i in range(ntotal)])

# 归一化（推荐用于 Inner Product 向量）
xb = xb / np.linalg.norm(xb, axis=1, keepdims=True)

# KMeans 聚类
n_clusters = 10  # 你可以改为 5、15、20 等试试看
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(xb)  # 聚类标签

# t-SNE 降维用于可视化
tsne = TSNE(n_components=2, random_state=42)
xb_2d = tsne.fit_transform(xb)

# 可视化聚类结果
plt.figure(figsize=(12, 8))
scatter = plt.scatter(xb_2d[:, 0], xb_2d[:, 1], c=cluster_labels, cmap='tab10', s=10, alpha=0.7)
plt.title(f"t-SNE of Car Vectors with KMeans Clustering (k={n_clusters})")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.colorbar(scatter, label='Cluster ID')
plt.tight_layout()
plt.show()
