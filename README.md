# Virtuoso Spectre E2B and Analog Design Bench Example

可分享的 Cadence EDA 环境启动代码，以及一道来自 **Analog Design Bench 网站**的完整公开题面、starter 和官方 verifier。用于同事复现环境、理解题目和开始设计；不包含已求解电路或模型评测成绩。

| 路线 | 工具与工艺 | 用途 |
|---|---|---|
| Cadence 环境验收 | Virtuoso IC251、Bridge、Spectre 25.1、analogLib | 新建 OA 分压器 → 原生网表导出 → DC 仿真 0.5 V |
| 官方 ADB 示例 | SKY130、ngspice、官方固定容器 | 设计五管 OTA，并按上游规格验证提交 |

这两条路线分别验证。Cadence 分压器通过不等于 ADB 题目通过；本仓库没有把 ngspice verifier 改成 Spectre，也没有将 SMIC 模型替换进 SKY130 题目。

## 目录

- `environment/template.json`：当前私有 E2B 模板身份及软件版本。
- `scripts/launch_e2b.py`：创建沙箱、运行时注入 license、执行真实 EDA smoke，默认销毁沙箱。
- `scripts/guest_smoke.py`：Virtuoso/Bridge 建图、Cadence SI 网表导出和 Spectre 仿真代码。
- `scripts/build_template.py`：从已获授权的 EDA 基础模板派生新模板。
- `examples/adb/sky130-ota-5t-gain40-pm60-noise50uv-pvt/`：官方示例原件。
- `scripts/run_adb.py`：构建官方 verifier 容器并验证你提供的候选电路。
- `docs/RUNNING.md`：环境配置、两条路线的运行与清理。
- `environment/repositories.json`：相关代码仓库和锁定版本。

## 快速开始

Python 启动代码建议使用 Python 3.11+；ADB 容器执行另需可运行 Linux 容器的 Docker。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -B scripts/verify_bundle.py
python -B -m unittest discover -s tests -v
```

### 运行 Virtuoso 和 Spectre

设置自己有权访问此模板的 E2B Key，以及部署方提供的 API/沙箱路由。配置示例在 `.env.example`，脚本从环境变量读取，不会自动加载 `.env`。

```bash
export E2B_API_KEY='你的 E2B Key'
export E2B_API_URL='http://hk-prod-e2b.xiaobei.top:3000'
export E2B_DOMAIN='hk-prod-e2b.xiaobei.top:3002'
python scripts/launch_e2b.py --license-file /安全目录/cadence.lic
```

默认从模板 `epwak9ve48ho1nu75llo` 创建沙箱。该模板仍是部署方的私有资源，公开 GitHub 仓库不自动赋予模板访问权限。API 地址和端口按实际网络调整；使用 envd relay 时额外设置 `E2B_SANDBOX_URL`。模板不可访问时，需要部署方授予权限或提供自己的基础模板。

成功后在 `output/e2b-smoke.json` 查看报告，包含实际 Bridge、OA、网表和 Spectre 结果。默认结束后销毁；使用 `--keep --timeout 3600` 可保留成功沙箱至指定超时。

### 开始 ADB 官方示例

选用题目：[Design a current-biased five-transistor OTA](https://analog-design-bench.tokenzhang.com/task/v2/sky130-ota-5t-gain40-pm60-noise50uv-pvt)。以 `instruction.md` 和官方 verifier 为准：1 pF 负载、50 µA 外部参考电流，在 27 个 PVT 组合检查环路增益、UGB、相位裕度、噪声与功耗，并在指定点检查 CMRR/PSRR。

先复制 starter，按题面设计自己的提交。starter 是待完成模板，不是达标答案。

```bash
mkdir -p output/design
cp examples/adb/sky130-ota-5t-gain40-pm60-noise50uv-pvt/environment/starter/circuit.spi output/design/circuit.spi
# 编辑 output/design/circuit.spi，并保留题面要求的 ota_5t 接口
python scripts/run_adb.py --candidate output/design/circuit.spi --dry-run
python scripts/run_adb.py --candidate output/design/circuit.spi --output output/adb-attempt-001
```

官方 Dockerfile 从固定 digest 的公开工具镜像获取 SKY130/ngspice。首次构建需要网络和镜像访问权限；评分容器使用 `--network none`，只读挂载候选电路，结果写入独立目录。每次使用新的空结果目录以避免误读旧结果。

Verifier 属于宿主评分代码，不应与参考答案一起交给待评测 Agent。本仓库不包含上游 `solution/` 和 `results/`。

## 环境如何分享

Git 保存启动和构建代码、环境身份、示例及说明；Cadence 软件数据保存在获授权的 E2B 私有模板中。License 在运行时注入，PDK 按所选流程另行提供。模拟软件、license、API Key、SMIC PDK 和大磁盘镜像都不存入 Git。

可在已有模板基础上派生一个独立私有模板：

```bash
python scripts/build_template.py --alias my-virtuoso-spectre --dry-run
python scripts/build_template.py --alias my-virtuoso-spectre
```

该代码复用已有软件安装，不从公开网络下载 Cadence，也不把工作过的、带 license/题目数据的沙箱固化为基础镜像。

## 来源和许可

官方题目来自 [Arcadia-1/analog-design-bench](https://github.com/Arcadia-1/analog-design-bench)，锁定提交 `972f7cd7c95381134387b250edf18f3bd23bdd25`。所选题面、starter 和 verifier 文件保持原字节；文件哈希见 `examples/adb/provenance.json`。

上游软件采用 Apache-2.0，benchmark 内容采用 **CC BY-NC 4.0**，商业使用需按上游许可取得相应授权；不能将整个仓库一概当作 Apache 内容。完整许可及来源通知位于 `licenses/`。原始 canary 声明及源码注释随上游文件保留。Cadence、SKY130、ngspice 等第三方依赖保留各自许可。

相关项目：[Virtuoso Bridge Lite](https://github.com/Arcadia-1/virtuoso-bridge-lite)、[E2B SDK](https://github.com/e2b-dev/E2B)。本仓库为独立集成示例，不是 Cadence 或 ADB 官方发行版。
