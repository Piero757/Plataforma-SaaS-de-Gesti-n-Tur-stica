import Redis from 'ioredis';
import { env } from './env';

let redisClient: Redis | null = null;

export function getRedisClient(): Redis {
  if (!redisClient) {
    redisClient = new Redis(env.REDIS_URL, {
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      lazyConnect: true,
    });

    redisClient.on('connect', () => console.log('✅ Redis conectado'));
    redisClient.on('error', (err) => console.error('❌ Redis error:', err));
    redisClient.on('reconnecting', () => console.warn('⚠️ Redis reconectando...'));
  }
  return redisClient;
}

export async function connectRedis() {
  const client = getRedisClient();
  await client.connect();
}

export async function disconnectRedis() {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
  }
}

// Helpers de cache
export const cache = {
  async get<T>(key: string): Promise<T | null> {
    const client = getRedisClient();
    const data = await client.get(key);
    if (!data) return null;
    return JSON.parse(data) as T;
  },

  async set(key: string, value: unknown, ttlSeconds = 300): Promise<void> {
    const client = getRedisClient();
    await client.setex(key, ttlSeconds, JSON.stringify(value));
  },

  async del(key: string): Promise<void> {
    const client = getRedisClient();
    await client.del(key);
  },

  async delPattern(pattern: string): Promise<void> {
    const client = getRedisClient();
    const keys = await client.keys(pattern);
    if (keys.length > 0) {
      await client.del(...keys);
    }
  },
};
