# Maintainer: Your Name <your.email@example.com>
pkgname=plasma-shortcut
pkgver=1.0.0
pkgrel=1
pkgdesc="Dolphin service menu to create .desktop shortcuts for any file or folder"
arch=('any')
url="https://github.com/yourusername/plasma-shortcut"
license=('GPL2')
depends=('kio' 'icoutils' 'pyside6')
install=plasma-shortcut.install
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    install -Dm755 src/dolphin-create-shortcut \
        "$pkgdir/usr/local/bin/dolphin-create-shortcut"

    install -Dm755 src/dolphin-edit-shortcut \
        "$pkgdir/usr/local/bin/dolphin-edit-shortcut"

    install -Dm755 src/dolphin-shortcut-dialog.py \
        "$pkgdir/usr/local/share/create-shortcut/dolphin-shortcut-dialog.py"

    sed "s|PREFIX|/usr/local|g" src/create-shortcut.desktop \
        > "$pkgdir/usr/share/kio/servicemenus/create-shortcut.desktop"
    chmod 755 "$pkgdir/usr/share/kio/servicemenus/create-shortcut.desktop"

    sed "s|PREFIX|/usr/local|g" src/edit-shortcut.desktop \
        > "$pkgdir/usr/share/kio/servicemenus/edit-shortcut.desktop"
    chmod 755 "$pkgdir/usr/share/kio/servicemenus/edit-shortcut.desktop"
}
