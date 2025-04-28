
# Material Icons 使用方式


## 基本使用：

```html
<i class="material-icons">home</i>
<i class="material-icons">search</i>
<i class="material-icons">menu</i>
```

## 不同尺寸：

```html
<!-- 预定义尺寸类 -->
<i class="material-icons md-18">face</i>
<i class="material-icons md-24">face</i>
<i class="material-icons md-36">face</i>
<i class="material-icons md-48">face</i>

<!-- 自定义尺寸 -->
<i class="material-icons" style="font-size: 60px">face</i>
```

## 颜色样式：

```html
<!-- 使用颜色类 -->
<i class="material-icons text-primary">star</i>
<i class="material-icons text-success">check</i>
<i class="material-icons text-warning">warning</i>
<i class="material-icons text-danger">error</i>

<!-- 直接设置颜色 -->
<i class="material-icons" style="color: #FF5733">favorite</i>
```


## 对齐方式：

```html
<!-- 使用颜色类 -->
<i class="material-icons align-middle">account_circle</i>
<i class="material-icons align-top">person</i>
<i class="material-icons align-bottom">group</i>

<!-- 在容器中居中 -->
<div class="d-flex align-items-center justify-content-center">
    <i class="material-icons">shopping_cart</i>
</div>
```

## 动画效果：

```html
<!-- 旋转动画 -->
<i class="material-icons rotating">refresh</i>
<i class="material-icons pulsing">notifications</i>

<style>
.rotating {
    animation: rotate 2s linear infinite;
}
.pulsing {
    animation: pulse 1s ease-in-out infinite;
}
</style>
```

## 在按钮中使用：

```html
<!-- 带图标的按钮 -->
<button class="btn btn-primary">
    <i class="material-icons">send</i>
    发送
</button>

<!-- 仅图标按钮 -->
<button class="btn btn-icon">
    <i class="material-icons">add</i>
</button>
```

## 列表中使用：

```html
<!-- 带图标的列表 -->
<ul class="list-unstyled">
    <li>
        <i class="material-icons">email</i>
        邮件
    </li>
    <li>
        <i class="material-icons">phone</i>
        电话
    </li>
</ul>
```


## 组合使用：

```html
<!-- 带徽章的图标 -->
<div class="position-relative">
    <i class="material-icons">notifications</i>
    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
        99+
    </span>
</div>
```


## 响应式使用：

```html
<!-- 响应式图标 -->
<i class="material-icons responsive-icon">dashboard</i>

<style>
.responsive-icon {
    font-size: 24px;
}

@media (min-width: 768px) {
    .responsive-icon {
        font-size: 36px;
    }
}
</style>
```

## 常用图标示例：

```html
<!-- 导航图标 -->
<i class="material-icons">menu</i>
<i class="material-icons">arrow_back</i>
<i class="material-icons">close</i>

<!-- 操作图标 -->
<i class="material-icons">edit</i>
<i class="material-icons">delete</i>
<i class="material-icons">save</i>

<!-- 状态图标 -->
<i class="material-icons">check_circle</i>
<i class="material-icons">error</i>
<i class="material-icons">help</i>
```
