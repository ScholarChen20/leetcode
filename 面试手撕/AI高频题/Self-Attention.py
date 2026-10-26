import numpy as np
def softmax(x, axis=-1):
    """
    x: 任意形状，沿 axis 做 softmax
    减去最大值防止 exp 溢出，这是面试必考点
    """
    x_shifted = x - np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x_shifted)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

def self_attention(Q, K, V, mask=None):
    """
    Q, K, V: (B, h, N, d_k)，已分好头或单头
    返回: output (B, h, N, d_k), attn_weights (B, h, N, N)
    """
    d_k = Q.shape[-1]
    scores = Q @ K.transpose(0, 1, 3, 2) / np.sqrt(d_k)  # (B,h,N,N)

    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)  # 掩码位置填极大负值

    attn_weights = softmax(scores, axis=-1)
    output = attn_weights @ V
    return output, attn_weights