#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Compare multiple gprof outputs")
    parser.add_argument(
        "--dir",
        "-d",
        default="results/exp_probe",
        help="Directory containing gprof_*.txt files",
    )
    parser.add_argument("--hostname", "-host", type=str, default="*")
    parser.add_argument(
        "--top", "-n", type=int, default=5, help="Number of top functions to display"
    )
    parser.add_argument(
        "--out", "-o", default="gprof_compare.png", help="Output image filename"
    )
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    path = Path(args.dir)
    files = sorted(path.glob(f"gprof_*_{args.hostname}.txt"))
    if not files:
        print(f"No files found in {args.dir}", file=sys.stderr)
        return

    stacked_df = build_stacked_dataframe(files, args.top)

    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111)
    cmap = plt.get_cmap("tab20")  # 20 色の ListedColormap
    n_segments = stacked_df.shape[0]  # 上位 top_n + 'others'
    colors = [cmap(i) for i in range(n_segments)]  # 0～n_segments-1 の色
    ax = stacked_df.T.plot(kind="bar", stacked=True, color=colors, ax=ax)
    
    
    for container, label in zip(ax.containers, stacked_df.index):
        # container はそのカテゴリ（label）に該当する全バーの矩形
        # labels を同じ文字列のリストで作成すると、各セグメントにカテゴリ名が入る
        label = shorten_label(label, 15)
        ax.bar_label(container,
                    labels=[label]*len(container),
                    label_type='center',
                    fontsize=8,
                    color='black',
                    rotation=0)

    ax.set_ylabel("Self Time (s)")
    ax.set_xlabel("Version@Host")
    ax.legend(
        title=f"Function (top {args.top}) + others",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(path / args.out)

    print(f"Saved comparison chart to {args.out}")


def shorten_label(name, maxlen=15, sep='_'):
    """
    アンダーバー区切りの name を、
    maxlen 以下に収まるよう後ろから順に各単語をイニシャル化して短縮します。
    """
    parts = name.split(sep)
    # 空文字パーツは除去
    parts = [p for p in parts if p]
    # まずまるごと組み立て
    cur = sep.join(parts)
    if len(cur) <= maxlen:
        return cur

    # 後ろから順にイニシャル化
    for i in range(len(parts)-1, -1, -1):
        if len(parts[i]) > 1:
            parts[i] = parts[i][0]  # イニシャルに
            cur = sep.join(parts)
            if len(cur) <= maxlen:
                return cur

    # ここまで縮めても長ければ末尾を切る
    return cur[:maxlen]


def build_stacked_dataframe(files, top_n):
    frames = {}
    for filepath in files:
        # parse version and host from filename: gprof_<version>_<host>.txt
        stem = filepath.stem  # e.g., "gprof_2.0.0_hpc1"
        rest = stem[len("gprof_") :]
        version, host = rest.split("_", 1)
        label = f"{version}@{host}"

        df = parse_gprof_flat(filepath)
        top = df.nlargest(top_n, "self_sec").set_index("name")["self_sec"]
        others = df["self_sec"].sum() - top.sum()
        series = top.copy()
        series["others"] = others
        frames[label] = series.to_dict()
    return pd.DataFrame(frames).fillna(0)


def parse_gprof_flat(filename):
    with open(filename) as f:
        lines = f.readlines()
    # Find the flat profile header
    start = next(
        i for i, l in enumerate(lines) if l.strip().startswith("%   cumulative")
    )
    cols = [
        "pcnt",
        "cum_sec",
        "self_sec",
        "calls",
        "self_s_call",
        "total_s_call",
        "name",
    ]
    data_lines = lines[start + 2 :]
    records = []
    for line in data_lines:
        if not line.strip():
            break
        parts = re.split(r"\s+", line.strip(), maxsplit=6)
        parts += [""] * (7 - len(parts))
        records.append(parts)
    df = pd.DataFrame(records, columns=cols)
    for c in cols[:-1]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


if __name__ == "__main__":
    main()
