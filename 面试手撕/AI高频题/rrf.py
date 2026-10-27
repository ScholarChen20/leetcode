def rrf(rank_lists, k=60):
    """
    :param rank_lists: list[list], 多个检索结果列表，[[doc1,doc2...], [docA,docB...]]
    :param k: RRF超参，默认60
    :return: 融合后排序好的文档列表，分数从高到低
    """
    score_dict = {}
    for lst in rank_lists:
        # rank从1开始
        for idx, doc in enumerate(lst, start=1):
            s = 1 / (k + idx)
            if doc in score_dict:
                score_dict[doc] += s
            else:
                score_dict[doc] = s
    # 按分数降序排序
    sorted_docs = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in sorted_docs]


# 测试示例
if __name__ == "__main__":
    list1 = ["d1", "d2", "d3", "d4"]
    list2 = ["d2", "d1", "d5", "d3"]
    res = rrf([list1, list2], k=60)
    print("RRF融合结果：", res)
