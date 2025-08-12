

// Função para gerar o código QR
function generateQR() {
    const ssid = document.querySelector('.ssid').value;
    const password = document.querySelector('.password').value;

    // Construir a sequência de dados do código QR WiFi
    const qrData = `WIFI:S:${ssid};T:WPA;P:${password};;`;

    // Atualizar a fonte da imagem do código QR
    const qrCodeImg = document.getElementById('qr-code');
    qrCodeImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=164x164&data=${encodeURIComponent(qrData)}`;
}

document.querySelector('.ssid').addEventListener('input', generateQR);
document.querySelector('.password').addEventListener('input', generateQR);

// Inicializar com um código QR padrão (opcional)
generateqr();