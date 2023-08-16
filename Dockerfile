FROM ubuntu:22.04 as builder

ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/London"
ENV user_name="runner"
ARG TARGETPLATFORM
ARG docker_ip
ARG user_pass
ARG package_name
ARG python_package

RUN ln -s /usr/bin/dpkg-split /usr/sbin/dpkg-split && \
    ln -s /usr/bin/dpkg-deb /usr/sbin/dpkg-deb && \
    ln -s /bin/rm /usr/sbin/rm && \
    ln -s /bin/tar /usr/sbin/tar && \
    ln -s /bin/as /usr/sbin/as

RUN apt-get update -y && \
    apt install -y python3 python3-dev python3-pip build-essential cmake git wget curl sshpass


RUN git config --global http.sslVerify "false"

RUN pip install conan==1.60.1

RUN conan profile new --detect default && \
    conan profile update settings.compiler.libcxx=libstdc++11 default

WORKDIR /usr/src/ustore-deps
COPY . /usr/src/ustore-deps

RUN git clone https://github.com/unum-cloud/ustore.git && \
    cd ustore/ && git checkout main-dev && git submodule update --init --recursive

# Disable ustore-deps package build
RUN sed -i 's/^\(.*\)cmake = CMake(self)/# \1cmake = CMake(self)/; s/^\(.*\)cmake.configure()/# \1cmake.configure()/; s/^\(.*\)cmake.build()/# \1cmake.build()\n       pass/' ./ustore/conanfile.py

RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        conan create ./ustore unum/x86_linux --build=missing && \
        cd ~/.conan && tar -czvf ustore_deps_x86_linux.tar.gz data/ && \
        sshpass -p "$user_pass" scp -o StrictHostKeyChecking=no ustore_deps_x86_linux.tar.gz ${user_name}@"$docker_ip":/home/${user_name}/work/ustore-deps/ustore-deps/; \
    elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        last_tag=$(curl https://api.github.com/repos/unum-cloud/ustore-deps/releases/latest | grep -i 'tag_name' | awk -F '\"' '{print $4}') && \
        wget -q https://github.com/unum-cloud/ustore-deps/releases/download/${last_tag}/"$package_name".tar.gz && \
        tar -xzf "$package_name".tar.gz -C ~/.conan && rm -rf "$package_name".tar.gz && \
        rm -rf ~/.conan/data/ustore* && \
        if [ "$python_package" = "True" ]; then \
            mv conanfile.py ./ustore; \
        fi && \
        conan create ./ustore unum/arm_linux --build=missing && \
        cd ~/.conan && tar -czvf "$package_name".tar.gz data/ && \
        sshpass -p "$user_pass" scp -o StrictHostKeyChecking=no "$package_name".tar.gz "$user_name"@"$docker_ip":/home/"$user_name"/work/ustore-deps/ustore-deps/ && \
        rm -rf "$package_name".tar.gz; \
    fi
