"""
HPLC-DAD 3D Chromatogram Viewer
================================
VSCode에서 바로 실행 가능한 순수 Python 스크립트입니다.
matplotlib 창이 뜨면 마우스로 드래그해서 자유롭게 회전/줌 할 수 있습니다.

[사전 준비]
1. VSCode에서 Python 확장 설치 확인
2. 터미널에서 아래 패키지 설치:
   pip install pandas numpy matplotlib

[사용 방법]
1. 아래 CSV_FILES 딕셔너리의 경로를 본인 PC의 실제 CSV 파일 경로로 수정
   (예: "C:/Users/이름/Desktop/DAD1A.CSV" 또는 "/Users/이름/Desktop/DAD1A.CSV")
2. VSCode에서 F5 또는 우측 상단 ▶ 버튼으로 실행
3. 뜨는 창에서 마우스 드래그로 회전, 스크롤로 줌 가능
4. 창을 닫지 않고 원하는 각도에서 저장하려면 창 상단의 저장(디스켓) 아이콘 클릭
5. 자동으로 360도 회전 mp4를 저장하고 싶으면 맨 아래 SAVE_ROTATION_VIDEO = True 로 변경
   (ffmpeg가 시스템에 설치되어 있어야 함: https://ffmpeg.org/download.html)
"""

import os
import pandas as pd
import numpy as np
import matplotlib

if os.environ.get("DISPLAY", "") == "" and os.environ.get("WAYLAND_DISPLAY", "") == "":
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.lines import Line2D

# ------------------------------------------------------------------
# 1) 파일 경로 & 파장 매핑
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "01_data", "Col"))
CSV_FILES = {
    243: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1A.CSV"),
    210: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1B.CSV"),
    225: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1C.CSV"),
    254: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1D.CSV"),
    262: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1E.CSV"),
    273: os.path.join(CSV_DIR, "2026-06-12 16-41-30+09-00-06.dx_DAD1F.CSV"),
}

# 회전 애니메이션(mp4)까지 자동 저장하려면 True로 변경 (ffmpeg 필요)
SAVE_ROTATION_VIDEO = False
OUTPUT_MP4_PATH = os.path.join(BASE_DIR, "hplc_3d_rotation.mp4")
OUTPUT_PNG_PATH = os.path.join(BASE_DIR, "hplc_3d_COL.png")

# ------------------------------------------------------------------
# 2) 디자인 설정
# ------------------------------------------------------------------
NAVY = "#1F3A5F"
BG = "#FFFFFF"


def load_data(csv_files: dict) -> tuple[list[int], np.ndarray, np.ndarray]:
    """CSV들을 읽어 (파장 리스트, time 배열, Z 행렬[mAU])을 반환."""
    data = {}
    for wl, path in csv_files.items():
        if not os.path.isfile(path):
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {path}")
        df = pd.read_csv(path, header=None, names=["time", "abs"])
        data[wl] = df

    wavelengths = sorted(csv_files.keys())
    time = data[wavelengths[0]]["time"].values
    z_matrix = np.array([data[wl]["abs"].values for wl in wavelengths])  # Absorbance in AU
    return wavelengths, time, z_matrix


def build_figure(wavelengths: list[int], time: np.ndarray, z_matrix: np.ndarray):
    """3D COL figure/axes 생성."""
    cmap = plt.get_cmap("viridis")
    colors = cmap(np.linspace(0.05, 0.95, len(wavelengths)))

    fig = plt.figure(figsize=(11, 6.5), dpi=120)
    fig.patch.set_facecolor(BG)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(BG)

    for i, wl in enumerate(wavelengths):
        x = time
        y = np.full_like(x, wl)
        z = z_matrix[i]

        ax.plot(x, y, z, color=colors[i], linewidth=1.4, zorder=i)

        poly_x = np.concatenate([x, x[::-1]])
        poly_z = np.concatenate([z, np.zeros_like(z)])
        verts = [list(zip(poly_x, np.full_like(poly_x, wl), poly_z))]
        ax.add_collection3d(
            Poly3DCollection(verts, facecolor=colors[i], alpha=0.12, edgecolor="none")
        )

    ax.set_xlabel("Retention Time (min)", fontsize=10, labelpad=10, color=NAVY, fontweight="bold")
    ax.set_ylabel("Wavelength (nm)", fontsize=10, labelpad=10, color=NAVY, fontweight="bold")
    ax.set_zlabel("Absorbance (AU)", fontsize=10, labelpad=8, color=NAVY, fontweight="bold")
    ax.set_yticks(wavelengths)
    ax.set_xlim(time.min(), time.max())
    ax.set_ylim(min(wavelengths) - 5, max(wavelengths) + 5)
    ax.set_zlim(bottom=0)
    ax.xaxis.pane.set_facecolor((1, 1, 1, 0))
    ax.yaxis.pane.set_facecolor((1, 1, 1, 0))
    ax.zaxis.pane.set_facecolor((1, 1, 1, 0))
    ax.grid(True, alpha=0.25)
    ax.set_title("HPLC-DAD 3D Chromatogram", fontsize=14, color=NAVY, fontweight="bold")
    ax.view_init(elev=25, azim=-60)

    handles = [
        Line2D([0], [0], color=colors[i], lw=2, label=f"{wl} nm")
        for i, wl in enumerate(wavelengths)
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 0.95),
              fontsize=8, frameon=False)

    summary_lines = []
    for i, wl in enumerate(wavelengths):
        idx = int(np.nanargmax(z_matrix[i]))
        rt = time[idx]
        peak_abs = z_matrix[i][idx]
        summary_lines.append(f"{wl} nm: RT={rt:.3f} min, Abs={int(round(peak_abs))} AU")

    summary_text = "\n".join(summary_lines)
    fig.text(
        0.98,
        0.03,
        summary_text,
        ha="right",
        va="bottom",
        fontsize=8,
        color=NAVY,
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none", "pad": 6},
    )

    return fig, ax


def save_rotation_video(fig, ax, out_path: str):
    """azimuth를 0~360도 회전시키며 mp4로 저장 (ffmpeg 필요)."""
    from matplotlib.animation import FuncAnimation

    def update(angle):
        ax.view_init(elev=25, azim=angle)
        return []

    anim = FuncAnimation(fig, update, frames=np.linspace(0, 360, 180), interval=50)
    anim.save(out_path, writer="ffmpeg", fps=20, extra_args=["-pix_fmt", "yuv420p"])
    print(f"[완료] 회전 애니메이션 저장: {out_path}")


def main():
    wavelengths, time, z_matrix = load_data(CSV_FILES)
    fig, ax = build_figure(wavelengths, time, z_matrix)

    # 정적 이미지 저장 (현재 view_init 각도 기준)
    fig.savefig(OUTPUT_PNG_PATH, dpi=300, facecolor=BG)
    print(f"[완료] 정적 이미지 저장: {OUTPUT_PNG_PATH}")

    if SAVE_ROTATION_VIDEO:
        save_rotation_video(fig, ax, OUTPUT_MP4_PATH)

    if plt.get_backend().lower() != "agg":
        print("창이 뜨면 마우스로 드래그해서 회전해보세요. 닫으면 스크립트가 종료됩니다.")
        plt.show()
    else:
        print("그래픽 디스플레이가 없으므로 이미지 파일만 저장했습니다.")


if __name__ == "__main__":
    main()