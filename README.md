# 说明
**在命令行上创建一个新的存储库**


----------


``` dockerfile
echo "# test" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/kxinter/test.git
git push -u origin master
```

**从命令行推送现有存储库**


----------

``` maxima
git remote add origin https://github.com/kxinter/test.git
git push -u origin master
```