// Manual Test Script for YouTube Quest Code Input
// Paste this into the browser console to test manually

console.log('🧪 MANUAL TEST SCRIPT LOADED');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

// Test 1: Check if code input section exists in DOM
function testCodeInputExists() {
    console.log('\n📋 TEST 1: Check if code input section exists');
    const codeInputSection = document.getElementById('codeInputSection');
    console.log('Element:', codeInputSection);
    console.log('Exists:', !!codeInputSection);
    
    if (codeInputSection) {
        console.log('Parent:', codeInputSection.parentElement);
        console.log('Classes:', codeInputSection.className);
        console.log('Style display:', codeInputSection.style.display);
        console.log('Computed display:', window.getComputedStyle(codeInputSection).display);
        console.log('✅ Element found');
    } else {
        console.log('❌ Element NOT found');
        console.log('Searching for similar elements...');
        const similar = document.querySelectorAll('[id*="codeInput"]');
        console.log('Found', similar.length, 'elements with "codeInput" in ID');
        similar.forEach((el, i) => {
            console.log(`  ${i+1}. id="${el.id}", display="${el.style.display}"`);
        });
    }
}

// Test 2: Try to show the code input manually
function testShowCodeInput() {
    console.log('\n📋 TEST 2: Manually show code input');
    const codeInputSection = document.getElementById('codeInputSection');
    
    if (codeInputSection) {
        console.log('Removing hidden class...');
        codeInputSection.classList.remove('hidden');
        
        console.log('Setting display to block...');
        codeInputSection.style.display = 'block';
        
        console.log('Setting visibility...');
        codeInputSection.style.visibility = 'visible';
        codeInputSection.style.opacity = '1';
        
        console.log('Adding border for visibility...');
        codeInputSection.style.border = '3px solid red';
        
        setTimeout(() => {
            console.log('After changes:');
            console.log('  Style display:', codeInputSection.style.display);
            console.log('  Computed display:', window.getComputedStyle(codeInputSection).display);
            console.log('✅ Changes applied - Check if you can see it now!');
        }, 100);
    } else {
        console.log('❌ Cannot show - element not found');
    }
}

// Test 3: Call the actual unlockCodeInput function
function testUnlockFunction() {
    console.log('\n📋 TEST 3: Call unlockCodeInput() function');
    if (typeof unlockCodeInput === 'function') {
        console.log('Function exists, calling...');
        unlockCodeInput();
        console.log('✅ Function called');
    } else {
        console.log('❌ unlockCodeInput function not found');
    }
}

// Test 4: Check dynamic content container
function testDynamicContent() {
    console.log('\n📋 TEST 4: Check dynamic content container');
    const container = document.getElementById('questDynamicContent');
    console.log('Container:', container);
    console.log('Container HTML length:', container?.innerHTML.length);
    console.log('Container visible:', container ? window.getComputedStyle(container).display !== 'none' : false);
    
    if (container) {
        console.log('Searching for code input within container...');
        const codeInput = container.querySelector('#codeInputSection');
        console.log('  Code input in container:', codeInput);
        console.log('✅ Container checked');
    } else {
        console.log('❌ Container not found');
    }
}

// Test 5: Check if we're on a YouTube quest
function testQuestType() {
    console.log('\n📋 TEST 5: Check current quest type');
    console.log('currentTask:', typeof currentTask !== 'undefined' ? currentTask : 'NOT DEFINED');
    console.log('currentTaskId:', typeof currentTaskId !== 'undefined' ? currentTaskId : 'NOT DEFINED');
    
    if (typeof currentTask !== 'undefined' && currentTask) {
        console.log('Task type:', currentTask.task_type);
        console.log('Task title:', currentTask.title);
        console.log('✅ Quest info available');
    } else {
        console.log('⚠️ No quest currently loaded');
    }
}

// Run all tests
function runAllTests() {
    console.log('🚀 RUNNING ALL TESTS...');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    testCodeInputExists();
    testDynamicContent();
    testQuestType();
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('✅ All tests complete');
    console.log('\nTo manually show code input, run: testShowCodeInput()');
    console.log('To call unlock function, run: testUnlockFunction()');
}

// Export functions to window for easy access
window.testCodeInputExists = testCodeInputExists;
window.testShowCodeInput = testShowCodeInput;
window.testUnlockFunction = testUnlockFunction;
window.testDynamicContent = testDynamicContent;
window.testQuestType = testQuestType;
window.runAllTests = runAllTests;

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('✅ Test functions loaded!');
console.log('\nAvailable commands:');
console.log('  runAllTests() - Run all diagnostic tests');
console.log('  testCodeInputExists() - Check if element exists');
console.log('  testShowCodeInput() - Force show the code input');
console.log('  testUnlockFunction() - Call the unlock function');
console.log('  testDynamicContent() - Check dynamic content container');
console.log('  testQuestType() - Check current quest type');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
