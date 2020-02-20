# ─── CONVERT JSON DATA INTO SQL FOR FAST RETRIVAL ───────────────────────────────
import scholarly


def get_docs(doc_ids: list):
    """ Get document meta info from database


    Arguments:
        doc_ids {list} -- [description]

    Return:
        A list of dictionary, the format of which is
        {
            author: ... ,
            time: , # the year in which it is published
            url:  the url of the paper
            desc: description(abstract)
            cited: citation number
            category: abbreviation list
        }
    """
    pass


def get_citations(article: dict):
    """Get the citation numbers from google scholar using scholarly and match the given paper with searched results

    Arguments:
        article {article} -- A dictionary containing paper metainfo
    """
    pass
