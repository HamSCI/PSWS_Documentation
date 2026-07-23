# THIS PAGE IS UNDER CONSTRUCTION

The standard antenna at the time of writing is the DX Engineering [RSEAV-1](https://www.dxengineering.com/parts/dxe-rseav-1).

For a roof installation: https://www.dxengineering.com/parts/dxe-rf-pro-1b

```mermaid
flowchart TD
    A[fa:fa-tower-cell GPS Antenna] -->|SMA| Bodnar(Bodnar GPSDO)
    Bodnar -->|Reference Clock Signal| RX888[RX888 SDR]
    Computer -->|5V USB Power| Bodnar
    HF[fa:fa-tower-cell HF Antenna] -->|F/F| CMC[Common Mode Choke]
    CMC -->|F/F| Bias[Bias Tee]
    Bias -->|Input F/F| LPF[Low Pass Filter]
    LPF --> |Out SMA/SMA| RX888
    RX888 --> |Data USB-B/USB-A| Computer
    Computer --> Peripherals[Peripherals fa:fa-computer-mouse fa:fa-desktop fa:fa-keyboard]
    Astron(Astron RS-12A, modified) --> |19V| Computer
```