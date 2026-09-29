/**
 * Cloudflare Worker: 24/7 Zero-Cost Serverless Telegram Bot
 * Mendukung deteksi otomatis file ZIP (Native Android & Flutter) + Live Log Preview
 */

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('TeleBuild Bot Webhook 24/7 Active', { status: 200 });
    }

    try {
      const update = await request.json();
      const message = update.message;
      if (!message) return new Response('OK');

      const chatId = message.chat.id;

      // Cek apakah pesan melampirkan file dokumen (ZIP)
      if (message.document && message.document.file_name?.toLowerCase().endsWith('.zip')) {
        const doc = message.document;
        const fileName = doc.file_name;

        // Ambil link download langsung file dari Telegram API
        const fileInfoResp = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/getFile?file_id=${doc.file_id}`);
        const fileInfo = await fileInfoResp.json();
        const directZipUrl = `https://api.telegram.org/file/bot${env.TELEGRAM_BOT_TOKEN}/${fileInfo.result.file_path}`;

        // Kirim status awal ke pengguna
        const initMsgResp = await sendTelegram(env.TELEGRAM_BOT_TOKEN, chatId,
          `📦 *Project ZIP Diterima:* `${fileName}`\n🔍 Mendeteksi struktur (Native Android / Flutter)...\n⚡ Memicu Runner GitHub Actions...`
        );
        const msgId = initMsgResp?.result?.message_id;

        // Trigger GitHub Actions dispatch
        await fetch(`https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/build-apk.yml/dispatches`, {
          method: 'POST',
          headers: {
            'User-Agent': 'Cloudflare-Worker-Telegram-Bot',
            'Authorization': `token ${env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ref: 'main',
            inputs: {
              source_type: 'zip_url',
              source_url: directZipUrl,
              build_type: 'release',
              chat_id: chatId.toString(),
              status_message_id: msgId ? msgId.toString() : '',
            },
          }),
        });

        return new Response('OK');
      }

      // Handle text command /start
      if (message.text && message.text.startsWith('/start')) {
        await sendTelegram(env.TELEGRAM_BOT_TOKEN, chatId,
          '🤖 *TeleBuild 24/7 Serverless (ZIP & Flutter Ready)*\n\n' +
          '• *Lampirkan file .ZIP* project Android Native atau Flutter untuk build otomatis.\n' +
          '• Atau kirim `/build <URL_GITHUB> [release|debug]`.'
        );
      }

      return new Response('OK');
    } catch (err) {
      return new Response(err.message, { status: 500 });
    }
  },
};

async function sendTelegram(token, chatId, text) {
  const resp = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: 'Markdown',
    }),
  });
  return await resp.json();
}
