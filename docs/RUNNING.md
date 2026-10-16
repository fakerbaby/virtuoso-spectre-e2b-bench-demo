# 运行与验证说明

## Cadence 路线

1. 取得能够访问私有软件模板的 E2B Key，按实际部署设置 API URL、domain 和可选 sandbox URL。
2. 准备自己的 Cadence license 文件。脚本先运行 bootstrap，建立 Rocky chroot、软件只读挂载和 secrets tmpfs，再写入 license，权限为 0600。
3. 执行 `python scripts/launch_e2b.py --license-file /path/cadence.lic`。
4. 验收代码通过 Bridge 在新 OA 库中建立 1 V 电源与两个 1 kΩ 电阻，保存原理图，调用 Cadence `si` 导出网表，再运行 Spectre DC 并检查 OUT=0.5 V。
5. 默认销毁沙箱。`--keep` 仅保留成功沙箱，失败时仍清理；保留的沙箱按创建时的 timeout 回收。

这一路线不需要私有 SMIC PDK。宿主的 `/opt/rocky/work` 对应 Rocky 内的 `/work`。从模板重启或恢复后重新检查挂载并按需注入 license，不假设 tmpfs secrets 可永久保留。

如需在私有模板内运行自己的 Python 工程脚本，可通过 E2B `files.write` 放入 `/opt/rocky/work`，再以 root 执行：

```bash
/opt/eda-bootstrap.sh /opt/venv/bin/python /work/your_script.py
```

## ADB 路线

官方示例依赖 SKY130/ngspice，而本 Cadence 软件模板不宣称内置这些依赖。这里通过官方容器运行示例，以保留原始工艺、模拟器和 verifier。

1. 阅读示例内 `instruction.md`、`task.toml` 和 `environment/starter/SKY130_NETLIST_GUIDE.md`。
2. 复制 starter 到自己的工作目录；编辑唯一提交物 `circuit.spi`，保留 `.subckt ota_5t vss ibias vdd vinn vinp vout` 接口。
3. 使用 `run_adb.py --dry-run` 检查将执行的 Docker 命令。
4. 实际执行时先构建官方 verifier image，再在独立无网络容器中运行 `/tests/test.sh`。
5. 从独立结果目录读取 `reward.json`。非空目录会被拒绝，以防旧结果污染。

若希望交互式使用官方 agent 环境：

```bash
docker build -t adb-ota-agent examples/adb/sky130-ota-5t-gain40-pm60-noise50uv-pvt/environment
docker run --rm -it --network none adb-ota-agent bash
```

Agent 容器与 verifier 容器独立。将最终 `circuit.spi` 导出后再交给评分脚本。不要把本仓库的 `tests/`、上游 verifier 或任何参考答案作为 Agent 的输入目录。

## Spectre 迁移的范围

不能仅将 SKY130/ngspice 文件后缀改成 `.scs`，或把器件模型替换为 SMIC，再称为同一道已验证 ADB 任务。Spectre 版本的任务需要另行核对 SKY130 模型兼容性、子电路/参数/单位、噪声与反馈测量语义、全部 PVT 以及裁判等价性。本次发布保留官方路径，未宣称完成该迁移。

## 常见问题

- E2B 401/403：核对 Key 所属部署和模板访问权限；公开仓库不提供模板凭据。
- E2B 路由不可达：根据所在网络设置部署方认可的 API、domain 和 envd relay；不要照抄别人的 localhost relay。
- Cadence license checkout 失败：检查当前文件、license server 可达性与可用 feature；源码仓库不包含 license。
- Docker 无法拉取官方工具镜像：检查 Docker 登录、网络、架构和镜像访问条件。固定 digest 不应被静默替换成其他镜像。
- ADB starter 得分为零：starter 尚未实现 OTA，是正常的待设计状态；环境启动成功不代表任务达标。
