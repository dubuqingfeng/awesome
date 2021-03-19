# coding=utf-8
import HTMLParser
import sys
from pymongo import MongoClient
import xml.dom.minidom as Dom

reload(sys)
sys.setdefaultencoding( "utf-8" )

client = MongoClient('mongodb://admin:mypass@192.168.99.100:27017/')


def createfile():
    doc = Dom.Document()
    root_node = doc.createElement("rss")
    root_node.setAttribute("version", "2.0")
    root_node.setAttribute("xmlns:excerpt", "http://wordpress.org/export/1.1/excerpt/")
    root_node.setAttribute("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    root_node.setAttribute("xmlns:wfw", "http://wellformedweb.org/CommentAPI/")
    root_node.setAttribute("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    root_node.setAttribute("xmlns:wp", "http://wordpress.org/export/1.1/")
    doc.appendChild(root_node)
    channel_node = doc.createElement("channel")
    wxr_version_node = doc.createElement("wp:wxr_version")
    wxr_version_value = doc.createTextNode("1.2")
    wxr_version_node.appendChild(wxr_version_value)

    for item in client.themeforest.themes.find():
        item_node = doc.createElement("item")
        item_title_node = doc.createElement("title")
        item_title_value = doc.createTextNode("<![CDATA[%s]]>" % item['Title'])
        item_title_node.appendChild(item_title_value)
        item_node.appendChild(item_title_node)
        wp_status_node = doc.createElement("wp:status")
        wp_status_value = doc.createTextNode("publish")
        wp_status_node.appendChild(wp_status_value)
        item_node.appendChild(wp_status_node)
        wp_type_node = doc.createElement("wp:post_type")
        wp_type_value = doc.createTextNode("post")
        wp_type_node.appendChild(wp_type_value)
        item_node.appendChild(wp_type_node)
        wp_is_sticky_node = doc.createElement("wp:is_sticky")
        wp_is_sticky_value = doc.createTextNode("0")
        wp_is_sticky_node.appendChild(wp_is_sticky_value)
        item_node.appendChild(wp_is_sticky_node)
        wp_post_date_node = doc.createElement("wp:post_date")
        wp_post_date_value = doc.createTextNode("2016-05-13 07:59:59")
        wp_post_date_node.appendChild(wp_post_date_value)
        item_node.appendChild(wp_post_date_node)
        content_encoded_node = doc.createElement("content:encoded")
        content_encoded_value = doc.createTextNode("<![CDATA[%s]]>" % item['Content'])
        content_encoded_node.appendChild(content_encoded_value)
        item_node.appendChild(content_encoded_node)
        category_node = doc.createElement("category")
        category_node.setAttribute("domain", "category")
        category = []
        for i in item['Category']:
            category.append(i)
        category_str = ' - '.join(category)
        print category_str
        category_node.setAttribute("nicename", category_str)
        category_value = doc.createTextNode("<![CDATA[%s]]>" % category_str)
        category_node.appendChild(category_value)
        item_node.appendChild(category_node)
        item_node.appendChild(create_meta(doc, "Preview URL", item['Preview URL']))
        item_node.appendChild(create_meta(doc, "Cover Image", item['Cover Image']))
        item_node.appendChild(create_meta(doc, "Price", item['Price']))
        item_node.appendChild(create_meta(doc, "Cover", item['Cover']))
        item_node.appendChild(create_meta(doc, "Url", item['Url']))
        item_node.appendChild(create_meta(doc, "Author URL", item['Author URL']))
        channel_node.appendChild(item_node)

    channel_node.appendChild(wxr_version_node)
    root_node.appendChild(channel_node)
    html_parser = HTMLParser.HTMLParser()
    tranform = html_parser.unescape(doc.toprettyxml(indent="\t", newl="\n", encoding="utf-8").decode('utf-8'))
    f = open("wordpress.xml", "w")
    f.write(tranform)
    f.close()


def create_meta(doc, node, value):
    wp_post_meta_node = doc.createElement("wp:postmeta")
    wp_meta_key_node = doc.createElement("wp:meta_key")
    wp_meta_key_value = doc.createTextNode(node)
    wp_meta_key_node.appendChild(wp_meta_key_value)
    wp_post_meta_node.appendChild(wp_meta_key_node)
    wp_meta_value_node = doc.createElement("wp:meta_value")
    wp_meta_value_value = doc.createTextNode(value)
    wp_meta_value_node.appendChild(wp_meta_value_value)
    wp_post_meta_node.appendChild(wp_meta_value_node)
    return wp_post_meta_node

if __name__ == '__main__':
    createfile()