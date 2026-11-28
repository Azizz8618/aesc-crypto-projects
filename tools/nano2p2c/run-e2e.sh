#!/bin/sh
# End-to-end evidence: nanolang -> C -> P2C -> BESM-6 module -> DUBNA run.
# The BESM-6 output is compared both with the native nanolang run and with
# the expected value supplied by the caller.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
NANOLANG=${NANOLANG:-/home/azizz/Yandex.Disk/nanolang}
PAS2C=${PAS2C:-/home/azizz/pas2c-metamorph}
DUBNA=${DUBNA:-/home/azizz/Yandex.Disk/besm6-new/dubna/build/dubna}
NANOC=${NANOC:-$NANOLANG/bin/nanoc}
SRC=${1:-$HERE/examples/arith.nano}
EXPECTED=${2:-42}
WORK=$(mktemp -d /tmp/nano2p2c-e2e.XXXXXX)

for needed in "$NANOC" "$HERE/nano2p2c.py" "$PAS2C/base" \
              "$PAS2C/reconstruct-bin-header.py" "$PAS2C/libc.bin" "$DUBNA" \
              "$PAS2C/dispak/runhotest.sh" "$PAS2C/dispak/env.sh" \
              "$PAS2C/dispak/passport.py"; do
    if [ ! -f "$needed" ]; then
        echo "run-e2e: missing prerequisite: $needed" >&2
        exit 2
    fi
done

cp "$PAS2C/base" "$PAS2C/reconstruct-bin-header.py" "$PAS2C/libc.bin" "$WORK/"
# Reuse the proven dispak single-test runner from pas2c in an isolated copy.
mkdir -p "$WORK/dispak"
cp "$PAS2C/dispak/runhotest.sh" "$PAS2C/dispak/env.sh" \
   "$PAS2C/dispak/passport.py" "$WORK/dispak/"

echo "workdir: $WORK"
echo "1. nanolang -> C"
"$NANOC" --target c "$SRC" -o "$WORK/program.c"

echo "2. C -> P2C (integer dialect)"
"$HERE/nano2p2c.py" "$WORK/program.c" -o "$WORK/program.p2c"
cat "$WORK/program.p2c"

echo "3. P2C -> BESM-6 object module"
sed 's/{/<:/g;s/}/:>/g' < "$WORK/program.p2c" > "$WORK/program.utxt"
(cd "$WORK" && ./base program.utxt program.o > program.compile.lst)
tail -c +7 "$WORK/program.o" > "$WORK/program.raw.o"
(cd "$WORK" && ./reconstruct-bin-header.py wrap --zones 16 \
    program.raw.o program.bin)
# DUBNA resource names are six characters, hence the short module name.
cp "$WORK/program.bin" "$WORK/prog.bin"

echo "4. native nanolang reference"
"$NANOC" "$SRC" -o "$WORK/native"
"$WORK/native" > "$WORK/native.out"

echo "5. BESM-6 execution under DUBNA"
cat > "$WORK/job.dub" <<'EOF'
*NAME nano2p2c
*disc:1/local
*file:prog,41
*file:libc,43
*perso:41
*perso:43,cont
*no load list
*execute
*end file
EOF
(cd "$WORK" && PATH="$(dirname "$DUBNA"):$PATH" dubna job.dub > run.lst 2>&1)
sed -n '/^\*EXECUTE/,/^---/p' "$WORK/run.lst" | sed '1d;$d' | sed '/^$/d' > "$WORK/besm6.out"

echo "native output: $(cat "$WORK/native.out")"
echo "BESM-6 output: $(cat "$WORK/besm6.out")"
# DUBNA prints through KOI-7 in upper case, so comparisons are case-folded.
tr '[:lower:]' '[:upper:]' < "$WORK/native.out" > "$WORK/native.norm"
tr '[:lower:]' '[:upper:]' < "$WORK/besm6.out" > "$WORK/besm6.norm"
printf '%s\n' "$EXPECTED" | tr '[:lower:]' '[:upper:]' > "$WORK/expected.out"
diff -u "$WORK/expected.out" "$WORK/besm6.norm"
diff -u "$WORK/native.norm" "$WORK/besm6.norm"
echo "PASS (DUBNA): nanolang and BESM-6 agree: $(cat "$WORK/besm6.out")"

echo "6. BESM-6 execution under dispak"
(cd "$WORK" && sh dispak/runhotest.sh "$WORK/program.p2c" > dispak.out 2>&1)
sed -n '/\*EXECUTE/,/КОНЕЦ ЗАДАЧИ/p' "$WORK/dispak.out" | sed '1d;$d' | sed '/^$/d' \
    > "$WORK/dispak.raw.out"
tr '[:lower:]' '[:upper:]' < "$WORK/dispak.raw.out" > "$WORK/dispak.norm"
diff -u "$WORK/expected.out" "$WORK/dispak.norm"
echo "PASS (dispak): nanolang and BESM-6 agree: $(cat "$WORK/dispak.raw.out")"
