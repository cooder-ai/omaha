# CUP加密编译控制说明（不修改代码方案）

## 概述
通过编译宏 `ENABLE_CUP_ENCRYPTION` 可以控制是否启用CUP加密功能，**无需修改任何现有代码**。

## 编译选项

### 启用CUP加密（默认）
```bash
# 默认启用CUP加密
ninja -C out/Debug

# 显式启用CUP加密
ninja -C out/Debug -DENABLE_CUP_ENCRYPTION=1
```

### 禁用CUP加密
```bash
# 禁用CUP加密
ninja -C out/Debug -DENABLE_CUP_ENCRYPTION=0
```

## 使用方法

### 1. 在需要控制CUP的地方包含头文件
```cpp
#include "omaha/common/cup_config.h"
```

### 2. 运行时检查
```cpp
if (IsCupEncryptionEnabled()) {
  // CUP加密已启用
} else {
  // CUP加密已禁用
}
```

### 3. 条件编译
```cpp
#if CUP_ENCRYPTION_ENABLED()
  // CUP加密相关代码
#else
  // 非CUP加密代码
#endif
```

## 手动控制方案

由于不修改现有代码，你可以通过以下方式手动控制：

### 方案1：修改编译参数
在构建时通过编译宏控制：
```bash
# 禁用CUP加密
ninja -C out/Debug -DENABLE_CUP_ENCRYPTION=0
```

### 方案2：临时修改代码
在 `omaha/goopdate/app_bundle_state_init.cc` 第126行：
```cpp
// 启用CUP加密
hr = web_service_client->Initialize(update_check_url, HeadersVector(), true);

// 禁用CUP加密  
hr = web_service_client->Initialize(update_check_url, HeadersVector(), false);
```

### 方案3：通过环境变量控制
在代码中添加环境变量检查：
```cpp
// 在 app_bundle_state_init.cc 中添加
bool use_cup = true;  // 默认启用
const char* cup_env = getenv("DISABLE_CUP_ENCRYPTION");
if (cup_env && strcmp(cup_env, "1") == 0) {
  use_cup = false;
}
hr = web_service_client->Initialize(update_check_url, HeadersVector(), use_cup);
```

## 影响范围

- **WebServicesClient**: 根据use_cup参数决定是否使用CupEcdsaRequest
- **网络请求**: 禁用CUP时使用SimpleRequest
- **安全性**: 禁用CUP会降低通信安全性

## 注意事项

1. **默认行为**: 默认启用CUP加密以保持安全性
2. **调试用途**: 禁用CUP主要用于调试和测试
3. **生产环境**: 建议在生产环境中保持CUP加密启用
4. **代码不变**: 此方案不需要修改任何现有代码，只需在需要时手动调整 