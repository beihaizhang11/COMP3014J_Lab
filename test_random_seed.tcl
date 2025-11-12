# 测试随机种子是否生效

set ns [new Simulator]

# 测试1: 设置随机种子
puts "Testing random seed..."

# 方法1: 使用RNG
set rng [new RNG]
$rng seed 12345
puts "RNG seed set to 12345"

# 方法2: 使用ns-random
ns-random 12345
puts "ns-random set to 12345"

# 创建随机变量测试
set ranvar [new RandomVariable/Uniform]
$ranvar use-rng $rng
$ranvar set min_ 0
$ranvar set max_ 100

# 生成10个随机数
puts "Random numbers:"
for {set i 0} {$i < 10} {incr i} {
    puts "  [$ranvar value]"
}

puts "Test completed"

