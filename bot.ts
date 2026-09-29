import { Bot } from 'grammy';
import { Octokit } from '@octokit/rest';

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '7824380847:AAGJ6ahNX4PtyDEw9LHSEgUF0KErzgcvyh0';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'YOUR_GITHUB_PAT';
const GITHUB_OWNER = process.env.GITHUB_OWNER || 'rkarifqi';
const GITHUB_REPO = process.env.GITHUB_REPO || 'apk-builder-runner';
const WORKFLOW_ID = 'build-apk.yml';

const bot = new Bot(BOT_TOKEN);
const octokit = new Octokit({ auth: GITHUB_TOKEN });

bot.command('start', async (ctx) => {
  await ctx.reply(
    `🤖 *TeleBuild APK Bot (Auto ZIP & Live Logs)*\n\n` +
    `• Cukup *lampirkan file .ZIP* project Native Android atau Flutter.\n` +
    `• Bot otomatis mendeteksi framework dan langsung mengompilasi APK!\n` +
    `• Preview log live akan di-stream ke pesan ini.`,
    { parse_mode: 'Markdown' }
  );
});

// Otomatis tangkap lampiran file ZIP
bot.on(':document', async (ctx) => {
  const doc = ctx.message.document;
  const fileName = doc.file_name || 'project.zip';

  if (!fileName.toLowerCase().endsWith('.zip')) {
    return ctx.reply('⚠️ Harap lampirkan file berekstensi .ZIP.');
  }

  const msg = await ctx.reply(`🔍 *Menganalisis Project ZIP:* `${fileName}`...\nMenyiapkan Cloud Runner...`, {
    parse_mode: 'Markdown',
  });

  try {
    const file = await ctx.api.getFile(doc.file_id);
    const directUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${file.file_path}`;

    await octokit.actions.createWorkflowDispatch({
      owner: GITHUB_OWNER,
      repo: GITHUB_REPO,
      workflow_id: WORKFLOW_ID,
      ref: 'main',
      inputs: {
        source_type: 'zip_url',
        source_url: directUrl,
        build_type: 'release',
        chat_id: ctx.chat.id.toString(),
        status_message_id: msg.message_id.toString(),
      },
    });

    await ctx.api.editMessageText(
      ctx.chat.id,
      msg.message_id,
      `🚀 *Kompilasi APK Dimulai!*\n\n` +
      `📦 *File:* `${fileName}`\n` +
      `⏳ Live preview log akan memperbarui pesan ini secara real-time.\n` +
      `📱 File .APK akan otomatis dikirim ke sini!`,
      { parse_mode: 'Markdown' }
    );
  } catch (err: any) {
    await ctx.api.editMessageText(ctx.chat.id, msg.message_id, `❌ Gagal: ${err.message}`);
  }
});

bot.start();
console.log('Bot Telegram APK Builder running 24/7 with ZIP auto-detection...');
