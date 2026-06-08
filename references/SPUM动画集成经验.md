# SPUM 动画集成实战经验

> 来源：成哥2026-06-07实战验证
> 状态：已验证的经验（非设计文档，是踩坑记录）

---

## 1. 核心陷阱：AnimatorController 不能置空

### 问题现象

用 Animancer Pro 或其他代码动画系统控制 SPUM 角色时，将 `runtimeAnimatorController` 设为 null 会导致角色卡死静止——动画不播放、部件不显示、角色像雕像一样钉在原地。

### 根因

SPUM 的 AnimatorController 不是普通的"动画播放器"，它是一个**完整的骨骼状态管理器**，承担了：
- 武器挂点激活/隐藏（左右手切换、武器类型切换）
- 身体部件的遮罩/Layer 混合（换装遮罩）
- 材质参数同步（换色、透明度渐变动画）
- 渲染组件的激活时序

强行置空 = 丢了以上全部管线。

### 正确做法

```csharp
// ❌ 错误：置空 Controller 用 Animancer 直接播
_spumPrefab.runtimeAnimatorController = null;
animancer.Play(clip);

// ✅ 正确：通过 SPUM 原生状态机驱动
_spumPrefab.OverrideControllerInit();  // 恢复 Controller
int stateIndex = TryFindStateAndIndex(clip, out PlayerState state, out int index);
_spumPrefab.PlayAnimation(state, index);  // 走 SPUM 原接口
```

### 兜底方案

对于 SPUM 状态列表中没有的自定义动画（如专属大招），通过覆盖 SPUM 的 OTHER 动画槽作为兜底播放。

### 推荐 Adapter 设计

```csharp
public class SPUMVisualAdapter {
    private SPUM_Animation _spumPrefab;
    
    public void PlayAnimation(AnimationClip clip) {
        if (TryFindStateAndIndex(clip, out PlayerState state, out int index)) {
            // 匹配到 SPUM 原生状态 → 用原生接口
            _spumPrefab.PlayAnimation(state, index);
        } else {
            // 未匹配 → 用 OTHER 槽兜底
            // 注意：不要动 runtimeAnimatorController
            PlayAsOtherSlot(clip);
        }
    }
    
    private bool TryFindStateAndIndex(AnimationClip clip, out PlayerState state, out int index) {
        // 遍历 SPUM 内部动画列表（IDLE / ATTACK / DAMAGED / 等）
        // 匹配 clip 名称或引用，返回对应 state + index
    }
}
```

---

## 2. UI 九宫格贴图：用 Unity Builtin 资源

### 问题现象

之前手写代码修改 Dropdown 颜色，结果出现大白块，UI 很丑。

### 根因

强行用代码给 `Dropdown` 贴纯色背景，没有使用 Unity 内置的 9-slice 贴图素材，导致拉伸变形、白块外露。

### 正确做法

```csharp
// 下拉框：用默认样式，不要手写颜色覆盖
var dropdown = DefaultControls.CreateDropdown(new DefaultControls.Resources());
// 这行就够了——Unity 内置 Dropdown 自带背景箭头贴图

// 九宫格圆角边栏
Sprite bgSprite = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/Background.psd");
Sprite btnSprite = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/UISprite.psd");

// 贴到 Image 组件上，Type = Sliced
panelImage.sprite = bgSprite;
panelImage.type = Image.Type.Sliced;
buttonImage.sprite = btnSprite;
buttonImage.type = Image.Type.Sliced;

// 半透明暗色底色（武侠风格）
panelImage.color = new Color(0.15f, 0.16f, 0.22f, 0.85f);
```

### 原理

- `Background.psd` 和 `UISprite.psd` 是 Unity Engine 内置的标准 UI 贴图，带圆角边框和立体感
- `Sliced`（九宫格拉伸）保证任意尺寸都不会糊边
- 不需要额外导入任何 UI 素材包

### 关键 API

| API | 用途 |
|-----|------|
| `AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/Background.psd")` | 面板背景 |
| `AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/UISprite.psd")` | 按钮贴图 |
| `DefaultControls.CreateDropdown(resources)` | 标准下拉框 |
| `Image.Type.Sliced` | 九宫格模式 |
