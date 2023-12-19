# -*- coding: utf-8 -*-
import json
from bigram import Bigram

class HMM:
    def __init__(self):
        self.load_param()
        self.bigram = Bigram()

    def load_param(self):
        self.init_prob = self.read('init_prob')
        self.emiss_prob = self.read('emiss_prob')
        self.trans_prob = self.read('trans_prob')
        self.pinyin_states = self.read('pinyin_states')

    def read(self, filename):
        with open('model_params/' + filename + '.json', 'r') as f:
            return json.load(f)

    # Viterbi process
    def trans(self, strs):

        # Note：不需要通过代码切分，直接输入时就以空格切分好
        seq = strs.split() #self.bigram.dp_search(strs)

        # smooth
        self.min_f = -3.14e+100 # 用于log平滑时所取的最小值，用于代替0
        length = len(seq)

        # https://github.com/night-killer/HMM_pinyin
        # pos 是目前节点的位置，word 为当前汉字即当前状态，
        # probability 为从 pre_word 上一汉字即上一状态转移到目前状态的概率
        # viterbi[pos][word] = (probability, pre_word)
        viterbi = {}
        for i in range(length):
            viterbi[i] = {}

        # initize
        # 针对每个拼音切分，首先根据第一个拼音，
        # 从 pinyin_states 中找出所有可能的汉字s，
        # 然后通过 init_prob 得出初始概率，通过 emiss_prob 得出发射概率，
        # 从而算出 viterbi[0][s]
        for s in self.pinyin_states.get(seq[0]):
            viterbi[0][s] = (
                self.init_prob.get(s, self.min_f) +
                self.emiss_prob.get(s, {}).get(seq[0], self.min_f) +
                self.trans_prob.get(s, {}).get('BOS', self.min_f)
            , -1
            )

        # DP
        # look trans_prob = {post1:{pre1:p1, pre2:p2}, post2:{pre1:p1, pre2:p2}}
        for i in range(length - 1):
            # 遍历 pinyin_states，找出所有可能与当前拼音相符的汉字 s，
            # 利用动态规划算法从前往后，推出每个拼音汉字状态的概率 viterbi[i+1][s]
            for s in self.pinyin_states.get(seq[i + 1]):
                viterbi[i + 1][s] = max([
                    (
                        viterbi[i][pre][0] +
                        self.emiss_prob.get(s, {}).get(seq[i + 1], self.min_f) +
                        self.trans_prob.get(s, {}).get(pre, self.min_f)
                    , pre
                    )
                    for pre in self.pinyin_states.get(seq[i])
                ])

        # 取概率最大的串（可从大到小取多个串），即概率最大的 viterbi[n][s]（s为末尾的汉字）
        for s in self.pinyin_states.get(seq[-1]):
            viterbi[length - 1][s] = (
                viterbi[length - 1][s][0] +
                self.trans_prob.get('EOS', {}).get(s, self.min_f)
                , viterbi[length - 1][s][1]
            )


        # 对串进行回溯即可得对应拼音的汉字
        words = [None] * length
        # 取概率最大的末尾汉字：比较的是 viterbi[length - 1][s]，但返回的是该值最大时的 s
        words[-1] = max(viterbi[length - 1], key=viterbi[length - 1].get)

        for n in range(length - 2, -1, -1):
            words[n] = viterbi[n + 1][ words[n + 1] ][1]

        return ''.join(w for w in words)


if __name__ == '__main__':
    '''
    HMM只考虑上一个字
    jiaohuaqiao
    xidazhijie
    '''
    # 测试
    hmm = HMM()
    for _ in range(5):
        print(hmm.trans(input('输入连续拼音（例如：nihao）：')))
