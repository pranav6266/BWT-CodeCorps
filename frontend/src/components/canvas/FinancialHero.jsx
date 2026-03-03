import { Canvas } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sphere, OrbitControls } from '@react-three/drei';

const FinancialHero = () => {
    return (
        <div className="h-[500px] w-full">
            <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1} />
                <Float speed={2} rotationIntensity={1.5} floatIntensity={2}>
                    <Sphere args={[1, 100, 200]} scale={1.8}>
                        <MeshDistortMaterial
                            color="#3b82f6" // Finance Blue
                            attach="material"
                            distort={0.4}
                            speed={2}
                        />
                    </Sphere>
                </Float>
                <OrbitControls enableZoom={false} />
            </Canvas>
        </div>
    );
};

export default FinancialHero;