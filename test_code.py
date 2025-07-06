from wordpress_xmlrpc import Client, WordPressPost
import os 
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.posts import EditPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import WordPressPost

def upload_product(name, description, short_description, regular_price, image_ids):
    """
    Upload a WooCommerce product using existing image IDs from the media library.
    
    :param name: str - Product title
    :param description: str - Full product description
    :param short_description: str - Short description
    :param regular_price: str - Price as a string (e.g., "29.99")
    :param image_ids: list - List of media IDs (first will be featured image)
    """

    url = "https://marazmetal.com"
    wp = Client(f"{url}/xmlrpc.php", "ali", "MarazAliDogan14#")

    catalog_visibility = "visible"
    tax_status = "taxable"
    stock_status = "instock"
    stock_quantity = 15

    post = WordPressPost()
    post.title = name
    post.content = description
    post.excerpt = short_description
    post.post_type = "product"
    post.terms_names = {
        'product_cat': ['Uncategorized'],
    }
    post.custom_fields = [
        {'key': '_regular_price', 'value': regular_price},
        {'key': '_price', 'value': regular_price},
        {'key': '_stock_status', 'value': stock_status},
        {'key': '_stock', 'value': str(stock_quantity)},
        {'key': '_manage_stock', 'value': 'yes'},
        {'key': '_visibility', 'value': catalog_visibility},
        {'key': '_tax_status', 'value': tax_status},
    ]
    post.post_status = 'publish'

    # Create the product
    post_id = wp.call(NewPost(post))
    print("✅ Product created successfully with ID:", post_id)

    # Now assign images (first = featured, rest = gallery)
    custom_fields = []
    if image_ids:
        custom_fields.append({'key': '_thumbnail_id', 'value': str(image_ids[0])})
        if len(image_ids) > 1:
            gallery_ids = ",".join(str(i) for i in image_ids[1:])
            custom_fields.append({'key': '_product_image_gallery', 'value': gallery_ids})

    if custom_fields:
        wp.call(EditPost(post_id, {'custom_fields': custom_fields}))
        print("✅ Product images updated.")


def update_product_images(post_id, media_ids, featured=None):
    """
    Update WooCommerce product images using XML-RPC.
    :param post_id: int - WooCommerce product ID
    :param media_ids: list of attachment IDs already uploaded to media library
    :param featured: optional int - ID of image to be set as featured image
    """
    wp = Client("https://marazmetal.com/xmlrpc.php", "ali", "MarazAliDogan14#")

    custom_fields = [
        {'key': '_product_image_gallery', 'value': ",".join(str(mid) for mid in media_ids)}
    ]

    if featured and featured in media_ids:
        custom_fields.append({'key': '_thumbnail_id', 'value': str(featured)})

    # Make the edit
    wp.call(EditPost(post_id, {
        'custom_fields': custom_fields
    }))

    print(f"✅ Product {post_id} image fields updated.")
upload_product("Test Product may 26","Simple dev description","Simple dev description","100",image_ids=[7273,7274,7275,7276])