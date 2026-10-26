import numpy as np
def kmeans(X, k, max_iters=100, tol=1e-4):
    """
    X: (N, D)
    返回: centers (k, D), labels (N,)
    """
    N, D = X.shape
    # 随机初始化中心（也可用 k-means++）
    idx = np.random.choice(N, k, replace=False)
    centers = X[idx].copy()

    for _ in range(max_iters):
        # 1. 分配簇：计算每个样本到各中心的距离，取最近
        # (N,1,D) - (k,D) -> (N,k,D) -> (N,k)
        dists = np.linalg.norm(X[:, np.newaxis, :] - centers, axis=2)
        labels = np.argmin(dists, axis=1)

        # 2. 更新中心
        new_centers = np.array([X[labels == i].mean(axis=0) for i in range(k)])

        # 3. 收敛判断
        if np.linalg.norm(new_centers - centers) < tol:
            break
        centers = new_centers

    return centers, labels