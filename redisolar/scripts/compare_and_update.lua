-- Redis script to compare a value stored in a hash field
-- and update it greater than or less than the provided
-- value, based on operation `op`.

local key = KEYS[1]
local field = ARGV[1]
local value = ARGV[2]
local op = ARGV[3]

local current = redis.call('hget', key, field)

if (current == false or current == nil) then
  redis.call('hset', key, field, value)
elseif op == '>' then
  if tonumber(value) > tonumber(current) then
    redis.call('hset', key, field, value)
  end
elseif op == '<' then
  if tonumber(value) < tonumber(current) then
    redis.call('hset', key, field, value)
  end
end
