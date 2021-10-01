#!/bin/bash
# Can be used as test environment while development

TRGT_DIR="test_content"

mkdir -p ${TRGT_DIR}/img
touch ${TRGT_DIR}/img/pic1.png

mkdir -p ${TRGT_DIR}/sub1/img
touch ${TRGT_DIR}/sub1/img/pic1.png
touch ${TRGT_DIR}/sub1/img/pic2.png

mkdir -p ${TRGT_DIR}/sub2

echo "
<html>
    <p>Text My Text </p>
    <a href="img/pic1.png"> very image </a>
    <div>
        <img src="img/pic1.png" />
    </div>
    <div>
        <a href="https://www.litres.ru"> Amazing external link </a>
    </div>

    <p>
        <a href="sub1/page.html"> local link </a>
    </p>

    <p>
        <a href="sub2/"> special link </a>
    </p>
</html>" >> test_content/index.html


echo "
<html>
    <ul>
    <li> <a href="img/pic1.png"> I 2.1 </a> </li>
    <li> <a href="img/pic2.png"> I 2.2 </a> </li> 
    <li> <a href="../img/pic1.png"> I 1 </a> </li>
</html>" >> test_content/sub1/page.html

echo "To launch local web server (with Docker), please launch the following command:"
echo "'docker run --name dev-nginx -v $PWD/test_content:/usr/share/nginx/html:ro -p 8080:80 -d nginx'"
