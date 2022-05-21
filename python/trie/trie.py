class TrieNode(object):
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.data = {}
        self.is_word = False


class Trie:
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.root = TrieNode()

    def insert(self, word):
        """
        Inserts a word into the trie.
        :type word: str
        :rtype: void
        """
        node = self.root
        for chars in word:
            child = node.data.get(chars)
            if not child:
                node.data[chars] = TrieNode()
            node = node.data[chars]
        node.is_word = True

    def search(self, word):
        """
        Returns if the word is in the trie.
        :type word: str
        :rtype: bool
        """
        node = self.root
        for chars in word:
            node = node.data.get(chars)
            if not node:
                return False
        return node.is_word  # 判断单词是否是完整的存在在trie树中


    def starts_with(self, prefix):
        """
        Returns if there is any word in the trie that starts with the given prefix.
        :type prefix: str
        :rtype: bool
        """
        node = self.root
        for chars in prefix:
            node = node.data.get(chars)
            if not node:
                return False
        return True

    def get_start(self, prefix):
        """
          Returns words started with prefix
          返回以prefix开头的所有words
          如果prefix是一个word，那么直接返回该prefix
          :param prefix:
          :return: words (list)
        """

        def get_key(pre, pre_node):
            word_list = []
            if pre_node.is_word:
                word_list.append(pre)
            for x in pre_node.data.keys():
                word_list.extend(get_key(pre + str(x), pre_node.data.get(x)))
            return word_list

        words = []
        if not self.starts_with(prefix):
            return words
        if self.search(prefix):
            words.append(prefix)
            return words
        node = self.root
        for chars in prefix:
            node = node.data.get(chars)
        return get_key(prefix, node)


if __name__ == '__main__':
    trie = Trie()

    print('trie.insert("apple"):', trie.insert("apple"))
    print('trie.insert("appal"):', trie.insert("appal"))
    print('trie.insert("appear"):', trie.insert("appear"))
    print('trie.insert("apply"):', trie.insert("apply"))
    print('trie.insert("appulse"):', trie.insert("appulse"))

    print('trie.search("apple"):', trie.search("apple"))  # 返回 True
    print('trie.search("app"):', trie.search("app"))  # 返回 False

    print('trie.startsWith("app"):', trie.starts_with("app"))  # 返回 True
    print('trie.insert("app"):', trie.insert("app"))
    print('trie.search("app"):', trie.search("app"))

    print('trie.search("app"):', trie.get_start("app"))
    print('trie.search("ap"):', trie.get_start('ap'))