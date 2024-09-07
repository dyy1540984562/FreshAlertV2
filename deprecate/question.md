# 用户询问记录

## 1. Linter Errors

### 问题描述
用户提供了一个文件 `fresh-alert/src/components/component.tsx`，并指出了代码中的错误：


### 解决方案
用户需要在前端代码中使用 `js-md5` 库进行MD5加密，并确保正确导入该库。

## 2. 前端登录时对密码进行MD5加密

### 问题描述
用户希望在前端对密码进行MD5加密，然后将加密后的密码发送到后端进行存储。

### 解决方案
在前端代码中添加 `js-md5` 库，并在登录和注册时对密码进行MD5加密

## 3. 添加图片上传和识别功能

### 问题描述
用户希望在前端添加一个可选项，可以上传图片，后端提供图片的识别接口，返回食物名称和保质期。

### 解决方案
在前端代码中添加图片上传功能，并调用后端的识别接口。

## 5. 优化后端代码

### 问题描述
用户希望优化后端代码，使其高内聚低耦合，代码更加简洁。

## 7. 前端代码优化

### 问题描述
用户希望在前端调用后端接口时参考 `foodService.ts` 文件，并在识别失败时显示警告。

### 解决方案
在前端代码中使用 `FoodService` 调用后端接口，并在识别失败时显示警告。



sudo apt-get install tesseract-ocr