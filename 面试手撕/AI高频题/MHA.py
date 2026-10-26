import numpy as np
from softmax import softmax
class MultiHeadAttention:
    def __init__(self, d_model, n_heads):
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        # 三个线性投影 + 输出投影
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01
        self.W_o = np.random.randn(d_model, d_model) * 0.01

    def _split_heads(self, x):
        # (B, N, d_model) -> (B, n_heads, N, d_k)
        B, N, _ = x.shape
        return x.reshape(B, N, self.n_heads, self.d_k).transpose(0, 2, 1, 3)

    def _merge_heads(self, x):
        # (B, n_heads, N, d_k) -> (B, N, d_model)
        B, _, N, _ = x.shape
        return x.transpose(0, 2, 1, 3).reshape(B, N, self.d_model)

    def forward(self, Q, K, V, mask=None):
        # 线性投影
        Q = self._split_heads(Q @ self.W_q)
        K = self._split_heads(K @ self.W_k)
        V = self._split_heads(V @ self.W_v)

        # 缩放点积注意力
        scores = Q @ K.transpose(0, 1, 3, 2) / np.sqrt(self.d_k)
        if mask is not None:
            scores = np.where(mask == 0, -1e9, scores)
        attn = softmax(scores, axis=-1)
        out = attn @ V

        # 拼接多头 + 输出投影
        out = self._merge_heads(out)
        return out @ self.W_o, attn