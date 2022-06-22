# See here for image contents: https://hub.docker.com/r/jupyter/datascience-notebook/

FROM jupyter/minimal-notebook

# We want to run common-debian.sh from here:
# https://github.com/microsoft/vscode-dev-containers/tree/main/script-library#development-container-scripts
# But that script assumes that the main non-root user (in this case jovyan)
# is in a group with the same name (in this case jovyan).  So we must first make that so.
COPY library-scripts/common-debian.sh /tmp/library-scripts/
USER root
RUN apt-get update \
 && groupadd jovyan \
 && usermod -g jovyan -a -G users jovyan \
 && bash /tmp/library-scripts/common-debian.sh \
 && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

# [Option 1] Install node and npm latest versions directly
#RUN apt-get install -y software-properties-common npm
#RUN npm install npm@latest -g && npm install n -g && n latest

# [Option 2] Install node and npm latest versions with NVM
#ENV NODE_VERSION=16.14.0
#ENV NVM_DIR=/home/jovyan/.nvm
#RUN apt install -y curl
#RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
#RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
#RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
#RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
#ENV PATH="/home/jovyan/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"


# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
 && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.password=''"]

USER jovyan