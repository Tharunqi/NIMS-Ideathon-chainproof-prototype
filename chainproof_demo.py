import hashlib
import json
import random
import time
from typing import List, Dict, Tuple
from datetime import datetime

class ShamirSecretSharing:
    """Simulates Shamir's Secret Sharing for update approval"""
    
    def __init__(self, total_shares: int, threshold: int):
        self.total_shares = total_shares
        self.threshold = threshold
        self.shares = {}
    
    def generate_shares(self, secret: str) -> Dict[str, str]:
        """Split the update signing key into multiple shares"""
        base_secret = hashlib.sha256(secret.encode()).hexdigest()
        
        shares = {}
        for i in range(1, self.total_shares + 1):
            share_data = f"{base_secret}-{i}-{int(time.time())}"
            share = hashlib.sha256(share_data.encode()).hexdigest()[:16]
            shares[f"entity_{i}"] = share
        
        self.shares = shares
        return shares
    
    def reconstruct_secret(self, provided_shares: Dict[str, str]) -> bool:
        """Check if threshold number of shares can reconstruct the key"""
        if len(provided_shares) < self.threshold:
            print(f"❌ Insufficient shares: {len(provided_shares)}/{self.threshold}")
            return False
        
        valid_shares = 0
        for entity, share in provided_shares.items():
            if entity in self.shares and self.shares[entity] == share:
                valid_shares += 1
        
        if valid_shares >= self.threshold:
            print(f"✅ Secret reconstructed successfully: {valid_shares}/{self.threshold} shares valid")
            return True
        else:
            print(f"❌ Secret reconstruction failed: {valid_shares}/{self.threshold} valid shares")
            return False

class ZeroTrustNetwork:
    """Simulates Zero Trust Network Architecture"""
    
    def __init__(self):
        self.microsegments = {}
        self.access_log = []
        self.blocked_count = 0
    
    def create_microsegment(self, segment_id: str, allowed_entities: List[str]):
        """Create isolated network segments"""
        self.microsegments[segment_id] = {
            'allowed_entities': allowed_entities,
            'traffic_encrypted': True
        }
        print(f"🔒 Created microsegment '{segment_id}' for {allowed_entities}")
    
    def verify_access(self, entity: str, target_segment: str, action: str) -> bool:
        """Verify every access request (Never Trust, Always Verify)"""
        if target_segment not in self.microsegments:
            return False
        
        allowed = entity in self.microsegments[target_segment]['allowed_entities']
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'entity': entity,
            'target': target_segment,
            'action': action,
            'allowed': allowed
        }
        self.access_log.append(log_entry)
        
        if allowed:
            print(f"✅ Access granted: {entity} -> {target_segment} ({action})")
        else:
            print(f"❌ Access denied: {entity} -> {target_segment} ({action})")
            self.blocked_count += 1
        
        return allowed

class AIAnomalyDetector:
    """AI-based anomaly detection for trading activity"""
    
    def __init__(self):
        # Normal trading ranges based on Indian markets
        self.normal_volume_range = (100, 5000)
        self.normal_frequency_range = (1, 15)
        self.normal_variance_range = (0.01, 0.3)
        self.anomaly_threshold = 0.3
    
    def detect_anomaly(self, current_trade: Dict) -> Tuple[bool, float]:
        """Detect if current trading activity is anomalous"""
        volume = current_trade.get('volume', 0)
        frequency = current_trade.get('frequency', 0)
        variance = current_trade.get('price_variance', 0)
        
        # Calculate anomaly scores for each parameter
        volume_score = 0
        if volume < self.normal_volume_range[0]:
            volume_score = (self.normal_volume_range[0] - volume) / self.normal_volume_range[0]
        elif volume > self.normal_volume_range[1]:
            volume_score = min((volume - self.normal_volume_range[1]) / self.normal_volume_range[1], 1.0)
        
        frequency_score = 0
        if frequency > self.normal_frequency_range[1]:
            frequency_score = min((frequency - self.normal_frequency_range[1]) / self.normal_frequency_range[1], 1.0)
        
        variance_score = 0
        if variance > self.normal_variance_range[1]:
            variance_score = min((variance - self.normal_variance_range[1]) / self.normal_variance_range[1], 1.0)
        
        # Combined weighted anomaly score
        anomaly_score = (volume_score * 0.4 + frequency_score * 0.3 + variance_score * 0.3)
        is_anomaly = anomaly_score > self.anomaly_threshold
        
        return is_anomaly, anomaly_score

def generate_market_data(trade_type="normal"):
    """Generate realistic market trading data"""
    stocks = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC']
    stock_prices = {'RELIANCE': 2450, 'TCS': 3200, 'HDFC': 1650, 'INFY': 1580, 'ITC': 340}
    
    stock = random.choice(stocks)
    
    if trade_type == "normal":
        return {
            'symbol': stock,
            'volume': random.randint(200, 3000),
            'frequency': random.randint(2, 12),
            'price_variance': random.uniform(0.02, 0.25),
            'price': stock_prices[stock] + random.uniform(-20, 20)
        }
    else:  # malicious
        return {
            'symbol': stock,
            'volume': random.randint(8000, 25000),
            'frequency': random.randint(50, 150),
            'price_variance': random.uniform(2.0, 8.0),
            'price': stock_prices[stock] + random.uniform(-200, 200)
        }

class ChainProofSystem:
    """Main system integrating all security layers"""
    
    def __init__(self):
        self.sss = ShamirSecretSharing(total_shares=5, threshold=3)
        self.ztna = ZeroTrustNetwork()
        self.anomaly_detector = AIAnomalyDetector()
        self.update_log = []
        self.circuit_breaker_active = False
        
        self.setup_zero_trust_segments()
    
    def setup_zero_trust_segments(self):
        """Configure Zero Trust network segments"""
        self.ztna.create_microsegment('vendor_zone', ['techtrader', 'marketsoft'])
        self.ztna.create_microsegment('exchange_zone', ['nse', 'bse', 'sebi'])
        self.ztna.create_microsegment('broker_zone', ['zerodha', 'upstox'])
        self.ztna.create_microsegment('regulator_zone', ['sebi', 'rbi'])
    
    def propose_software_update(self, vendor: str, update_package: str, is_attack=False) -> bool:
        """Simulate secure software update process"""
        print(f"\n📄 Software Update Proposed by {vendor}")
        print(f"📦 Update Package: {update_package}")
        
        # Step 1: Zero Trust verification
        if not self.ztna.verify_access(vendor, 'vendor_zone', 'update_proposal'):
            return False
        
        # Step 2: Generate shares for quorum approval
        secret_key = f"update_{datetime.now().timestamp()}"
        shares = self.sss.generate_shares(secret_key)
        
        # Step 3: Simulate approval process
        approval_shares = {}
        
        if is_attack:
            # Malicious actor only has vendor access
            print("\n💀 Malicious actor attempting update with limited access...")
            approval_shares['vendor'] = shares.get("entity_1", "")
        else:
            # Legitimate update gets proper approvals
            print(f"\n🏛️ Seeking approvals from regulatory authorities...")
            
            entities = ['sebi', 'nse', 'auditor']
            approvals_needed = 2
            
            approved_entities = random.sample(entities, approvals_needed)
            for entity in approved_entities:
                if self.ztna.verify_access(entity, 'exchange_zone', 'update_approval'):
                    approval_shares[entity] = shares.get(f"entity_{hash(entity) % 5 + 1}", "")
                    print(f"✅ {entity.upper()} approved the update")
            
            # Vendor's share
            approval_shares['vendor'] = shares.get("entity_1", "")
        
        # Step 4: Reconstruct secret with quorum
        if self.sss.reconstruct_secret(approval_shares):
            print("🎉 Update APPROVED and cryptographically signed!")
            self.log_update(update_package, 'approved', list(approval_shares.keys()))
            return True
        else:
            print("🚫 Update REJECTED - insufficient cryptographic approval")
            self.log_update(update_package, 'rejected', list(approval_shares.keys()))
            return False
    
    def monitor_trading_activity(self, num_trades=3):
        """Monitor trading activity for anomalies"""
        print(f"\n📊 Monitoring {num_trades} trading activities...")
        
        for i in range(num_trades):
            # Generate mix of normal and suspicious trades
            if random.random() < 0.4:  # 40% chance of malicious trade
                trade_data = generate_market_data("malicious")
                print(f"Trade {i+1}: {trade_data['symbol']} - Vol: {trade_data['volume']}, Freq: {trade_data['frequency']}")
            else:
                trade_data = generate_market_data("normal")
                print(f"Trade {i+1}: {trade_data['symbol']} - Vol: {trade_data['volume']}, Freq: {trade_data['frequency']}")
            
            is_anomaly, score = self.anomaly_detector.detect_anomaly(trade_data)
            
            if is_anomaly:
                print(f"🚨 ANOMALY DETECTED! Score: {score:.3f}")
                print("🛑 Triggering circuit breaker - Trading paused for investigation")
                self.circuit_breaker_active = True
                return False
            else:
                print(f"✅ Trade appears normal. Anomaly score: {score:.3f}")
        
        return True
    
    def log_update(self, package: str, status: str, approvers: List[str]):
        """Log update attempts"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'package': package,
            'status': status,
            'approvers': approvers
        }
        self.update_log.append(log_entry)
    
    def get_security_report(self):
        """Generate system security report"""
        total_requests = len(self.ztna.access_log)
        blocked_requests = self.ztna.blocked_count
        
        print(f"\n📊 CHAINPROOF SECURITY REPORT")
        print(f"=" * 40)
        print(f"Network Access Requests: {total_requests}")
        print(f"Blocked Access Attempts: {blocked_requests}")
        print(f"Update Attempts: {len(self.update_log)}")
        print(f"Circuit Breaker Status: {'ACTIVE' if self.circuit_breaker_active else 'INACTIVE'}")

def simulate_attack_scenario():
    """Demonstrate how ChainProof prevents supply chain attacks"""
    print("=" * 60)
    print("CHAINPROOF SUPPLY CHAIN SECURITY SIMULATION")
    print("=" * 60)
    
    # Initialize the secure system
    chainproof = ChainProofSystem()
    
    # Scenario 1: Legitimate update
    print("\n" + "="*50)
    print("SCENARIO 1: LEGITIMATE SOFTWARE UPDATE")
    print("="*50)
    legitimate_approved = chainproof.propose_software_update('techtrader', 'security_patch_v2.1', is_attack=False)
    
    # Scenario 2: Malicious update attempt (compromised vendor)
    print("\n" + "="*50)
    print("SCENARIO 2: MALICIOUS UPDATE ATTEMPT")
    print("="*50)
    print("🏴‍☠️ Attacker compromised vendor's system and tries to push malware")
    
    malicious_approved = chainproof.propose_software_update('techtrader', 'malware_update', is_attack=True)
    
    if not malicious_approved:
        print("🛡️ ChainProof PREVENTED the malicious update!")
        print("🔒 Multi-party approval requirement stopped the attack")
    
    # Scenario 3: Anomaly detection in trading
    print("\n" + "="*50)
    print("SCENARIO 3: REAL-TIME ANOMALY DETECTION")
    print("="*50)
    
    # Normal trading first
    print("📈 Normal market trading:")
    normal_trades = True
    for i in range(2):
        trade = generate_market_data("normal")
        is_anomaly, score = chainproof.anomaly_detector.detect_anomaly(trade)
        print(f"Trade: {trade['symbol']} | Volume: {trade['volume']} | Score: {score:.3f}")
        if is_anomaly:
            normal_trades = False
    
    # Normal trading first
    print("📈 Normal market trading:")
    for i in range(2):
        trade = generate_market_data("normal")
        is_anomaly, score = chainproof.anomaly_detector.detect_anomaly(trade)
        print(f"Trade: {trade['symbol']} | Volume: {trade['volume']} | Variance: {trade['price_variance']:.3f} | Score: {score:.3f}")
        if is_anomaly:
            print(f"🚨 Unexpected anomaly in normal trade!")
        else:
            print("✅ Normal trade confirmed")
    
    print("\n📊 Generating some malicious trades for demonstration:")
    for i in range(2):
        malicious_trade = generate_market_data("malicious")
        is_anomaly, score = chainproof.anomaly_detector.detect_anomaly(malicious_trade)
        print(f"Malicious Trade: {malicious_trade['symbol']} | Volume: {malicious_trade['volume']} | Freq: {malicious_trade['frequency']} | Score: {score:.3f}")
        if is_anomaly:
            print(f"🚨 CORRECTLY DETECTED as anomalous!")
        else:
            print("❌ Failed to detect (adjust threshold)")
    
    if normal_trades:
        print("✅ Normal trade analysis complete")
    
    # Suspicious trading (simulating post-attack scenario)
    print("\n⚠️ Suspicious trading activity detected:")
    chainproof.monitor_trading_activity(3)
    
    # Generate security report
    chainproof.get_security_report()
    
    print("\n" + "="*50)
    print("SIMULATION SUMMARY")
    print("="*50)
    print("✅ Shamir's Secret Sharing: Prevents single-point compromise")
    print("✅ Zero Trust Architecture: Limits lateral movement")
    print("✅ AI Anomaly Detection: Catches malicious activity in real-time")
    print("✅ Multi-layered defense: Comprehensive supply chain protection")
    print("\n" + "="*50)
    print("CHAINPROOF - Securing Markets Through Cryptographic Trust")
    print("="*50)

if __name__ == "__main__":
    simulate_attack_scenario()