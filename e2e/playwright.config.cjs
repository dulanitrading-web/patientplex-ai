const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
  testDir:'.',testMatch:'*.spec.cjs',workers:1,retries:0,timeout:120000,
  expect:{timeout:15000},
  reporter:[['list'],['html',{open:'never'}],['junit',{outputFile:'test-results/junit.xml'}]],
  use:{browserName:'chromium',baseURL:'http://localhost:3000',viewport:{width:1440,height:900},screenshot:'only-on-failure',trace:'retain-on-failure',video:'retain-on-failure'}
});
