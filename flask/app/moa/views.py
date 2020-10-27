from flask import Blueprint, Response
from flask import current_app as app
from flask_restful import Api, Resource
import markdown
import os
#from .. import db

moa = Blueprint('moa', __name__)
api = Api(moa)



@moa.route('/')
def moa_home():
    """Present some documentation"""

    # Open the README file
    with open(os.path.join(moa.root_path) + '/README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        md = markdown.markdown(content, extensions=['tables','fenced_code'])
        return md

