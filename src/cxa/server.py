import json
import os
import shutil
import tempfile
from pathlib import Path
from wsgiref import simple_server

import falcon
from falcon_cors import CORS

try:
    from transformer import TemplateVariableValidation, handleGit, run
except ModuleNotFoundError:
    from .transformer import TemplateVariableValidation, handleGit, run


def onerror(func, path, exc_info):
    import stat

    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def make_error(res, error_text, errors=[]):
    res.status = falcon.HTTP_BAD_REQUEST
    res.body = json.dumps({"success": False, "error": error_text, "errors": errors})


cors = CORS(allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)


class TransformationResource:
    def on_post(self, req, res):
        ipt = req.media
        try:
            git_repo_dir = tempfile.mkdtemp()
            handleGit(ipt["gitURL"], git_repo_dir)
            run(git_repo_dir, git_repo_dir, ipt.get("template_variables", dict()))

            output_zip = tempfile.mktemp()
            output_zip_full = output_zip + ".zip"
            shutil.make_archive(output_zip, "zip", git_repo_dir)

            try:
                shutil.rmtree(git_repo_dir, onerror=onerror)
            except:
                pass

            res.content_type = "application/zip"
            res.stream = open(output_zip_full, "rb")
            os.remove(output_zip_full)
        except TemplateVariableValidation as e:
            make_error(res, str(e), e.errors)
        except KeyError:
            make_error(res, "Invalid JSON")
        except Exception as e:
            make_error(res, str(e))


api = falcon.API(middleware=[cors.middleware])
api.add_route("/transform", TransformationResource())
api.add_static_route("/", os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../static/")))

if __name__ == "__main__":
    httpd = simple_server.make_server("127.0.0.1", 8000, api)
    httpd.serve_forever()
