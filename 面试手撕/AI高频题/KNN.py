import numpy as np
def knn_classify(X_train, y_train, X_test, k=3):
    """
    X_train: (N, D), y_train: (N,)
    X_test:  (M, D)
    返回: preds (M,)
    """
    # 批量计算测试集到训练集的欧氏距离
    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
    test_sq = np.sum(X_test ** 2, axis=1, keepdims=True)      # (M,1)
    train_sq = np.sum(X_train ** 2, axis=1, keepdims=True).T  # (1,N)
    dists = np.sqrt(test_sq + train_sq - 2 * X_test @ X_train.T)  # (M,N)

    # 取最近的 k 个训练样本，多数投票
    knn_idx = np.argsort(dists, axis=1)[:, :k]
    preds = np.array([np.bincount(y_train[idx]).argmax() for idx in knn_idx])
    return preds
