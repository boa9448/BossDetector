import os


cur_dir = os.path.abspath(os.path.join(__file__))
models_dir = os.path.abspath(os.path.join(cur_dir, "models"))

embed_model_path = os.path.abspath(os.path.join(models_dir, "openface_nn4.small2.v1.t7"))