import numpy as np
def softmax(x, axis=-1):
    """
    x: 任意形状，沿 axis 做 softmax
    减去最大值防止 exp 溢出，这是面试必考点
    """
    x_shifted = x - np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x_shifted)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

# 交叉熵损失（常一起考）
def cross_entropy(pred, target):
    # pred: softmax 输出 (N, C), target: 类别索引 (N,)
    N = pred.shape[0]
    log_pred = -np.log(pred[np.arange(N), target] + 1e-12)
    return np.mean(log_pred)