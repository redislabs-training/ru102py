-- Lua script to compare set if lower
-- key: the name a Redis string storing a number
-- new: a number which, if smaller, will replace the existing number
local key = KEYS[1]
local new = ARGV[1]
local current = redis.call('GET', key)
if (current == false) or
   (tonumber(new) < tonumber(current)) then
  redis.call('SET', key, new)
  return 1
else
  return 0
end
