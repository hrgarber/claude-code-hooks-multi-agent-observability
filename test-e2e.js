import puppeteer from 'puppeteer';
import { exec } from 'child_process';
import { promisify } from 'util';
import assert from 'assert';

const execAsync = promisify(exec);

async function test() {
  console.log('🧪 Starting E2E test for Claude Code Observability...\n');
  
  try {
    // 1. Verify services are up
    console.log('1️⃣ Checking server health...');
    const health = await fetch('http://localhost:4000/health');
    assert(health.ok, 'Server should be healthy');
    console.log('✅ Server is healthy\n');

    // 2. Open dashboard
    console.log('2️⃣ Opening dashboard...');
    const browser = await puppeteer.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Set desktop viewport (1024px+ for desktop layout)
    await page.setViewport({ width: 1280, height: 800 });
    
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
    console.log('✅ Dashboard loaded\n');
    
    // 3. Verify connected
    console.log('3️⃣ Verifying WebSocket connection...');
    await page.waitForFunction(
      () => {
        const spans = Array.from(document.querySelectorAll('span'));
        return spans.some(span => span.textContent === 'Connected');
      },
      { timeout: 5000 }
    );
    console.log('✅ Dashboard connected to server\n');
    
    // 4. Send test event directly to server
    console.log('4️⃣ Sending test event to server...');
    const testId = Date.now();
    const testMessage = `test observability ${testId}`;
    console.log(`   Test message: "${testMessage}"`);
    
    // Send event directly to server (simulating what hooks would do)
    try {
      const response = await fetch('http://localhost:4000/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_app: 'test-e2e',
          session_id: `test-session-${testId}`,
          hook_event_type: 'UserPromptSubmit',
          payload: {
            prompt: testMessage,
            timestamp: new Date().toISOString()
          }
        })
      });
      console.log('✅ Test event sent to server\n');
    } catch (error) {
      console.error('❌ Failed to send test event:', error);
    }
    
    // 5. Wait for UserPromptSubmit event to appear
    console.log('5️⃣ Waiting for event to appear in dashboard...');
    await page.waitForFunction(
      () => {
        const spans = Array.from(document.querySelectorAll('span'));
        return spans.some(span => span.textContent?.includes('UserPromptSubmit'));
      },
      { timeout: 10000 }
    );
    console.log('✅ UserPromptSubmit event appeared\n');
    
    // 6. Click the latest event to expand
    console.log('6️⃣ Expanding event details...');
    const events = await page.$$('.group.relative.p-4');
    await events[events.length - 1].click();
    console.log('✅ Event expanded\n');
    
    // 7. Verify our test prompt is in the payload
    console.log('7️⃣ Verifying test message in payload...');
    await page.waitForFunction(
      (msg) => {
        const pres = Array.from(document.querySelectorAll('pre'));
        return pres.some(pre => pre.textContent?.includes(msg));
      },
      { timeout: 5000 },
      testMessage
    );
    console.log('✅ Test message found in event payload\n');
    
    console.log('🎉 All tests passed! Observability system is working correctly.');
    await browser.close();
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
test().catch(error => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});