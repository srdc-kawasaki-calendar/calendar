# NC Calendar
NC Calendarは，工作機械の予約を Discord で行うボット．  
このマニュアルの指示通りにコードを書いても正常に動作してくれなかった場合，**必ず**IT係か作者に連絡してください．なお，改善案があれば遠慮なく提案してください．

# 利用方法
## プレフィックス
```
k! <コマンド> <パラメータ>
```
コマンドを入力するときにテキストの文頭に `k!` をつける  
## 予約の追加
コマンドフォーマット
```
k! nc <NCの名前> <開始日付> <開始時間> <経過時間もしくは終了時間> <コメント>
```
`NCの名前`<span style="color:red">（必須項目）</span>
- NCのリスト表
    ```
    マコト:['m','M','makoto']
    ミニマコト:['mm','MM','minimakoto']
    匠:['t','T','takumi']
    大黒:['ok','OK','ookuro','ookiikuroiyatsu']
    大きい黒いやつ:['k','K','kuro','kuroiyatsu']
    鉄のおもちゃ:['to','TO','tetsunoomo']
    ```
- リストの中のいずれでも大丈夫です．但し，日本語は**避けてください**  
- 例：`k! nc takumi` ← 匠に指定

`開始日付`<span style="color:red">（必須項目）</span>
- `月-日` の形で入力する
- 例：`k! nc takumi 6-13` ← 6月13日に指定  
    <span style="color:orange">※注意</span> `06-13` の表記もできる

`開始時間`<span style="color:red">（必須項目）</span>
- `時-分` の形で入力する
- 例：`k! nc takumi 6-13 8:02` ← （午前）8時2分に指定  
    <span style="color:red">※注意</span> 24時間制なので注意してください．`12:14` 分は昼の12時14分になる  
    <span style="color:orange">※注意</span> `08:02` の表記もできる

`経過時間もしくは終了時間`<span style="color:red">（必須項目）</span>
- 経過時間を入力する場合，`時h分` の形で入力する <span style="color:green">（推奨）</span>
    - 例：`k! nc takumi 6-13 8:02 3h0` ← 切削時間は3時間0分に指定  
    <span style="color:orange">※注意</span> `03h00` の表記もできる 
    - 日付がどれくらい変わるほど長くでも大丈夫です
- 終了時間を入力する場合，`時:分` の形で入力する  
    - 例：`k! nc takumi 6-13 8:02 20:02` ← 終了時間は当日の20時2分に指定  
    <span style="color:orange">※注意</span> 終了日付は開始日付と同じ

 `コメント`<span style="color:grey">（任意項目）</span>
 - `スペースが入ってもいい文字列` の形で入力する
 - 例：`k! nc takumi 7-3 8:02 12h14 いじめは よくない` ← コメントを「いじめは よくない」に指定
 
 ### サンプル
 NC予約/マコト/8月5日/9時0分/55時55分間/もんくある？
 ```
 k! nc m 08-05 9:00 55h55 もんくある？
 ```  