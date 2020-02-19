# ttds_group

记得先安装 `pip install -r requirements.txt`

## 术语

Posting/Posting List 不用说了。

Posting list group：每一个 term 对应一个 posting list；现在将一部分 term 映射到同一个 key 上【可以使用[hash](https://docs.python.org/3.7/library/hashlib.html)】，相同的 key 的 posting list组成一个Posting list group。group的作用是分割 index 文件大小，其应该用一个 dict 实现，dict 里的 key 是 term，value 是 posting list 。存在磁盘上应该用比特数组化（compress）后的结果。

`cached_posting_list`：已读进内存的 posting list group 的缓存。可以使用`cachetools`包。



`config_template.yaml`: 配置文件模板，将里面的参数设置成适合本地环境的样子，然后复制成新文件`config.yaml`即可使用。

`cat_abbr_full.txt`：分类简写-全称的表格。